/*
 *  Unix SMB/CIFS implementation.
 *  NBT netbios routines and daemon - version 2
 *
 *  Copyright (C) Guenther Deschner 2011
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef _NMBD_NMBD_H_
#define _NMBD_NMBD_H_

#ifndef HAVE_PIPE
#define SYNC_DNS 1
#endif

#include "libsmb/nmblib.h"
#include "nmbd/nmbd_proto.h"

#define NMBD_WAIT_INTERFACES_TIME_USEC  (250 * 1000)

/****************************************************************************
true if two IPv4 addresses are equal
****************************************************************************/

#define ip_equal_v4(ip1,ip2) ((ip1).s_addr == (ip2).s_addr)

#endif /* _NMBD_NMBD_H_ */
