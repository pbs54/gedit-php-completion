# -*- coding: utf-8 -*-

#  phpdb.py - PHP completion using the completion framework
#  
#  Copyright (C) 2009 - Jesse van den Kieboom
#  Copyright (C) 2009 - Ignacio Casal Quinteiro
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import sqlite3
import os
import sys

class PHPDb:
    def __init__(self, database):
        self.db = None

        if os.path.isfile(database):
            try:
                self.db = sqlite3.connect(database)
            except:
                pass

    def function_info(self, fid):
        if not self.db:
            return ''

        try:
            result = self.db.execute('SELECT `name`, `optional`, `type` FROM arguments WHERE `function` = ? ORDER BY `index`', (fid,))
        except Exception as e:
            sys.stderr.write("PHPCompletion: Error in query: %s\n" % (str(e), ))
            return ''

        ret = ''

        for arg in result:
            name = ('%s %s' % (arg[2], arg[0])).strip()
            if ret != '':
                if arg[1]:
                    ret += ' <i>[, %s]</i>' % (name,)
                    continue
                else:
                    ret += ', '

            if arg[1]:
                ret += '<i>[, %s]</i>' % (name,)
            else:
                ret += name

        return ret

    def complete(self, query, maxresults, arg1, arg2 = None):
        if not self.db:
            return []

        if maxresults > 0:
            extra = 'LIMIT %d' % (maxresults,)
        else:
            extra = ''

        try:
            query = query % (extra,)
            if not arg1:
                result = self.db.execute(query)
            else:
                if not arg2:
                    result = self.db.execute(query, (arg1,))
                else:
                    result = self.db.execute(query, (arg1, arg2))
        except Exception as e:
            sys.stderr.write("PHPCompletion: Error in query: %s\n" % (str(e), ))
            return []
        
        return list(result)
    
    def complete_function(self, func, maxresults = -1):
        query = "SELECT `id`, `name`, `description`, `short_description` FROM functions WHERE `class` = 0 AND `name` LIKE ? || '%%' ORDER BY `name` %s"
        
        return self.complete(query, maxresults, func)
    
    def complete_const(self, const, maxresults = -1):
        query = "SELECT `id`, `name` FROM constants WHERE `class` = 0 AND `name` LIKE ? || '%%' ORDER BY `name` %s"
        
        return self.complete(query, maxresults, const)
    
    def complete_class(self, class_name, maxresults = -1):
        if not class_name:
            query = "SELECT `id`, `name`, `doc` FROM classes %s"
        else:
            query = "SELECT `id`, `name`, `doc` FROM classes WHERE `name` LIKE ? || '%%' ORDER BY `name` %s"
        
        return self.complete(query, maxresults, class_name)

    def complete_class_const(self, class_name, const, maxresults = -1):
        class_query = "SELECT `id` FROM classes where `name` = ? %s"
        class_id = self.complete(class_query, 1, class_name)
        
        result = []
        if class_id:
            if not const:
                query = "SELECT `id`, `name` FROM constants WHERE `class` = ? %s"
                result = self.complete(query, maxresults, class_id[0][0])
            else:
                query = "SELECT `id`, `name` FROM constants WHERE `class` = ? AND `name` LIKE ? || '%%' ORDER BY `name` %s"
                result = self.complete(query, maxresults, class_id[0][0], const)
        
        return result

# ex:ts=4:et:
