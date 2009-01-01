# Copyright (C) 2006 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import time, config

class Benchmarker(object):
    def __init__(self):
        self.start = time.clock()
        self.last  = self.start
        self.bench = []

    def snapshot(self, handle, caption):
        self.bench.append((handle, caption, time.clock() - self.last))
        self.last = time.clock()

    def snapshot_total(self, handle, caption):
        self.bench.append((handle, caption, time.clock() - self.start))

    def get_html(self):
        result = ''
        for handle, caption, snapshot in self.bench:
            try:
                if not config.cfg.getboolean('benchmark',
                                             'show_%s_time' % handle):
                    continue
            except:
                continue
            result += '<tr>'
            result += ' <td class="benchmark" id="%s" align="center">' % handle
            result += ' %s' % (caption % snapshot)
            result += ' </td>'
            result += '</tr>'
        if result == '':
            return ''
        return '<table width="100%">' + result + '</table>'
