#!/usr/bin/env python3
# Unix SMB/CIFS implementation.
# Copyright (C) Stefan Metzmacher 2020
# Copyright (C) 2021 Catalyst.Net Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os

from ldb import SCOPE_SUBTREE
from samba.dcerpc import security
from samba.ndr import ndr_unpack
from samba.samba3 import libsmb_samba_internal as libsmb
from samba.samba3 import param as s3param

from samba.tests.krb5.kdc_base_test import KDCBaseTest

sys.path.insert(0, "bin/python")
os.environ["PYTHONUNBUFFERED"] = "1"

global_asn1_print = False
global_hexdump = False


class SmbTests(KDCBaseTest):
    """Test for SMB authentication using Kerberos credentials stored in a
       credentials cache file.
    """

    def test_smb(self):
        # Create a user account and a machine account, along with a Kerberos
        # credentials cache file where the service ticket authenticating the
        # user are stored.

        user_name = "smbusr"
        mach_name = self.dns_host_name
        service = "cifs"
        share = "tmp"

        # Create the user account.
        (user_credentials, _) = self.create_account(user_name)

        # Talk to the KDC to obtain the service ticket, which gets placed into
        # the cache. The machine account name has to match the name in the
        # ticket, to ensure that the krbtgt ticket doesn't also need to be
        # stored.
        (creds, cachefile) = self.create_ccache_with_user(user_credentials,
                                                          mach_name,
                                                          service)

        # Set the Kerberos 5 credentials cache environment variable. This is
        # required because the codepath that gets run (gse_krb5) looks for it
        # in here and not in the credentials object.
        krb5_ccname = os.environ.get("KRB5CCNAME", "")
        self.addCleanup(os.environ.__setitem__, "KRB5CCNAME", krb5_ccname)
        os.environ["KRB5CCNAME"] = "FILE:" + cachefile.name

        # Authenticate in-process to the machine account using the user's
        # cached credentials.

        # Retrieve the user account's SID.
        ldb_res = self.ldb.search(scope=SCOPE_SUBTREE,
                                  expression="(sAMAccountName=%s)" % user_name,
                                  attrs=["objectSid"])
        self.assertEqual(1, len(ldb_res))
        sid = ndr_unpack(security.dom_sid, ldb_res[0]["objectSid"][0])

        # Connect to a share and retrieve the user SID.
        s3_lp = s3param.get_context()
        s3_lp.load(self.lp.configfile)

        min_protocol = s3_lp.get("client min protocol")
        self.addCleanup(s3_lp.set, "client min protocol", min_protocol)
        s3_lp.set("client min protocol", "NT1")

        max_protocol = s3_lp.get("client max protocol")
        self.addCleanup(s3_lp.set, "client max protocol", max_protocol)
        s3_lp.set("client max protocol", "NT1")

        conn = libsmb.Conn(mach_name, share, lp=s3_lp, creds=creds)

        (uid, gid, gids, sids, guest) = conn.posix_whoami()

        # Ensure that they match.
        self.assertEqual(sid, sids[0])

        # Remove the cached credentials file.
        os.remove(cachefile.name)


if __name__ == "__main__":
    global_asn1_print = True
    global_hexdump = True
    import unittest
    unittest.main()