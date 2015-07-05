#
# QuakeC Tokenizer
#   Barry Pederson <bpederson@geocities.com>
#
# $Id: qc2python.py,v 1.5 2001/02/05 21:15:44 barryp Exp $
#
import os, pprint, string, re, types

translator_info = '$Id: qc2python.py,v 1.5 2001/02/05 21:15:44 barryp Exp $'[1:-1]

############ Output Filter ###########################
class VectorFilter:
    def __init__(self, outfile):
        self._outfile = outfile
        self._buffer = ''
        self._x = re.compile('(.*?)\.x\s*=\s*(.*)', re.S)
        self._y = re.compile('(.*?)\.y\s*=\s*(.*)', re.S)
        self._z = re.compile('(.*?)\.z\s*=\s*(.*)', re.S)
        self._augment = re.compile('(?P<indent>\s*)(?P<var>\S+)\s*=\s*(?P=var)\s*(?P<op>\\+|\\-|\\*|/|&|\\|)\s*(?P<val>.*)')
        self._paren = paren = re.compile('\([^()]*\)')
        self._lower_precedence = {'*': '+-&|', 
                                  '/': '*/+-&|',
                                  '+': '&|',
                                  '-': '&|+',
                                  '&': '|',
                                  '|': ''}
        
    def __del__(self):
        self.flush()
                
    def write(self, s):
        self._buffer += s
        
    def flush(self):
        test = string.strip(self._buffer)
        if test and (test[0] != '#'):
            self._filter()
        self._outfile.write(self._buffer)
        self._outfile.flush()
        self._buffer = ''            
        
    def _filter(self):
        m = self._x.match(self._buffer)
        if m:
            self._buffer = '%s %%= Vector(%s, None, None)' % (m.group(1), m.group(2))
            return
        m = self._y.match(self._buffer)
        if m:
            self._buffer = '%s %%= Vector(None, %s, None)' % (m.group(1), m.group(2))
            return
        m = self._z.match(self._buffer)
        if m:
            self._buffer = '%s %%= Vector(None, None, %s)' % (m.group(1), m.group(2))
            return
            
        m = self._augment.match(self._buffer)
        if m:
            #
            # This code may be potentially rewritten as an augmented
            # assignment, (such as 'i = i + 1' -> 'i += 1')
            #
            # Make sure that augmenting this line won't 
            # screw up operator precendence. For example, we don't want:  
            # 'a = a * 3 + 1' to turn into 'a *= 3 + 1'
            # So we need to make sure there are no operators of lower 
            # precendence on the right side of  augmented assignment
            #
            op = m.group('op')
            val = m.group('val')

            #
            # Things hidden inside paretheses are ok, so simplify
            # the augmentation value to hide them, so for example, 
            #   a = a * (3 + 1)
            # is temporarily converted to: 'a = a * x', so when we
            # look for lower precedence operators like '+' we won't see
            # them.
            #             
            oldval = val
            newval = self._paren.sub('x', oldval)
            while newval != oldval:
                oldval = newval
                newval = self._paren.sub('x', oldval)
                
            #
            # Look for bad stuff and bail if found with a warning
            #                
            for ch in newval:
                if ch in self._lower_precedence[op]:
                    print '  Warning: will not rewrite:', string.strip(self._buffer)
                    print '                         as:', '%s %s= %s' % (m.group('var'), op, val)
                    print "     In Python (and real C), '%s' has a lower precedence than '%s'" % (ch, op)
                    print '     (this may be a bug in the original QuakeC code, and perhaps the rewritten code would be correct)'
                    return
                    
            #
            # no need for parens around the rvalue
            #                    
            while (val[0] == '(') and (val[-1] == ')'):
                val = val[1:-1]                
            
            #print 'Rewrote:', string.strip(self._buffer)
            self._buffer = '%s%s %s= %s' % (m.group('indent'), m.group('var'), op, val)    
            #print '     as:', string.strip(self._buffer)
                        


############# Tokenizer ##############################

# built-in string type is used for strings
class QC_Token:
    def __init__(self, s):
        self.value = s
        self.attr = None
        self.body = None
    def __repr__(self):
        return self.value
        
class Identifier(QC_Token): pass
class Number(QC_Token): pass
class Operator(QC_Token): pass

class Comment(QC_Token):
    def __repr__(self):
        return '# %s' % self.value
        
class Vector(QC_Token):
    def __repr__(self):
        return 'Vector(%s)' % string.join(string.split(self.value), ', ')
        
class Newline(QC_Token):
    def __init__(self, s = '\n'):
        self.value = '\n'
        self.attr = None
        
class Semicolon(QC_Token):
    def __init__(self, s = ';'):
        self.value = ';'
        self.attr = None
       
def is_token(t, v):
    return isinstance(t, QC_Token) and (t.value == v)

_digits = '0123456789'
_delimiters = '!&()*+,-/:;<=>|[]{} \t\r\n'
_keywords = ['if', 'else', 'while', 'do', 'return', 'local', 
             'void', 'float', 'string', 'vector', 'entity',
             '.void', '.float', '.string', '.vector', '.entity']

_STATE_START         = 0
_STATE_IDENTIFIER    = 1
_STATE_OR            = 2
_STATE_AND           = 3
_STATE_NOT           = 4
_STATE_EQUAL         = 5
_STATE_LESS          = 6
_STATE_GREATER       = 7
_STATE_SLASH         = 8
_STATE_SLASH_SLASH   = 9
_STATE_SLASH_STAR    = 10
_STATE_SLASH_STAR_STAR   = 11
_STATE_INTEGER           = 12
_STATE_FLOAT             = 13
_STATE_STRING            = 14
_STATE_STRING_ESCAPE     = 15
_STATE_VECTOR            = 16
_STATE_MINUS             = 17

class Tokenizer:
    def _accumulate(self, ch):
        self._accum += ch
        if ch == '\n':
            self._linenum += 1
        
    def _kick_string(self):
        self._kick_object(self._accum)

    def _kick_newline(self):
        n = Newline()
        n.linenum = self._linenum
        self._kick_object(n)        
        self._linenum += 1
        
    def _kick(self, other_type = None, s = None):
        if s == None:
            s = self._accum
        if other_type == None:
            if s in _keywords:
                other_type = Operator
            else:
                other_type = Identifier
        self._kick_object(other_type(s))
        
    def _kick_object(self, obj):
        self._result.append(obj)
        self._accum = ''
        self._state = _STATE_START        

    def tokens(self, s):
        self._result = []
        self._accum = ''
        self._state = _STATE_START
        self._linenum = 1
        for ch in s:
            self._parse_char(ch)
        self._parse_char('\n') # final whitespace to kick dangling bits out
        return self._result

    def _parse_char(self, ch):        
        if self._state == _STATE_START:
            if ch == '/':
                self._state = _STATE_SLASH
            elif ch in ' \t':
                pass
            elif ch == '\r':
                pass
            elif ch == '\n':
                self._kick_newline()
            elif ch in _digits:
                self._accumulate(ch)
                self._state = _STATE_INTEGER
            elif ch == '"':
                self._state = _STATE_STRING
            elif ch == '\'':
                self._state = _STATE_VECTOR
            elif ch == '=':
                self._state = _STATE_EQUAL
            elif ch == '<':
                self._state = _STATE_LESS
            elif ch == '>':
                self._state = _STATE_GREATER
            elif ch == '!':
                self._state = _STATE_NOT
            elif ch == '&':
                self._state = _STATE_AND
            elif ch == '|':
                self._state = _STATE_OR
            elif ch == '-':
                self._state = _STATE_MINUS
            elif ch == ';':
                self._kick(Semicolon)
            elif ch in _delimiters:
                self._kick(Operator, ch)
            else:
                self._accumulate(ch)
                self._state = _STATE_IDENTIFIER
        elif self._state == _STATE_IDENTIFIER:
            if ch in _delimiters:
                self._kick()
                self._parse_char(ch)
            else:
                self._accumulate(ch)
        elif self._state == _STATE_OR:
            if ch == '|':
                self._kick(Operator, '||')
            else:
                self._kick(Operator, '|')
                self._parse_char(ch)
        elif self._state == _STATE_AND:
            if ch == '&':
                self._kick(Operator, '&&')
            else:
                self._kick(Operator, '&')
                self._parse_char(ch)
        elif self._state == _STATE_NOT:
            if ch == '=':
                self._kick(Operator, '!=')
            else:
                self._kick(Operator, '!')
                self._parse_char(ch)
        elif self._state == _STATE_EQUAL:
            if ch == '=':
                self._kick(Operator, '==')
            else:
                self._kick(Operator, '=')
                self._parse_char(ch)
        elif self._state == _STATE_LESS:
            if ch == '=':
                self._kick(Operator, '<=')
            else:
                self._kick(Operator, '<')
                self._parse_char(ch)
        elif self._state == _STATE_GREATER:
            if ch == '=':
                self._kick(Operator, '>=')
            else:
                self._kick(Operator, '>')
                self._parse_char(ch)
        elif self._state == _STATE_SLASH:
            if ch == '*':
                self._state = _STATE_SLASH_STAR
            elif ch == '/':
                self._state = _STATE_SLASH_SLASH
            else:
                self._kick(Operator, '/')
                self._parse_char(ch)
        elif self._state == _STATE_SLASH_SLASH:
            if ch == '\n':
                self._kick(Comment)
                self._parse_char(ch)
            else:
                self._accumulate(ch)        
        elif self._state == _STATE_SLASH_STAR:
            if ch == '*':
                self._state = _STATE_SLASH_STAR_STAR
            else:
                self._accumulate(ch)
        elif self._state == _STATE_SLASH_STAR_STAR:
            if ch == '/':
                self._kick(Comment)
            else:
                self._accumulate('*')
                if ch != '*':
                    self._accumulate(ch)
                    self._state = _STATE_SLASH_STAR
        elif self._state == _STATE_INTEGER:
            if ch in _digits:
                self._accumulate(ch)
            elif ch == '.':
                self._accumulate(ch)
                self._state = _STATE_FLOAT
            else:
                self._kick(Number)
                self._parse_char(ch)
        elif self._state == _STATE_FLOAT:
            if ch in _digits:
                self._accumulate(ch)
            else:
                self._kick(Number)
                self._parse_char(ch)
        elif self._state == _STATE_STRING:
            if ch == '\\':
                self._state = _STATE_STRING_ESCAPE
            elif ch == '"':
                self._kick_string()
            else:
                self._accumulate(ch)
        elif self._state == _STATE_STRING_ESCAPE:
            if ch == 'n':
                self._accumulate('\n')
                self._state = _STATE_STRING
            else:
                self._accumulate(ch)
                self._state = _STATE_STRING
        elif self._state == _STATE_VECTOR:
            if ch == '\'':
                self._kick(Vector)
            else:
                self._accumulate(ch)
        elif self._state == _STATE_MINUS:
            if ch in _digits:
                self._accumulate('-')
                self._accumulate(ch)
                self._state = _STATE_INTEGER
            else:
                self._kick(Operator, '-')
                self._parse_char(ch)
        else:
            print 'Unknown state', self._state

######### End of Tokenizer #####################

class QC_Module:
    def __init__(self, s, basename):
        self.basename = basename
        self.import_list = []
        tokens = Tokenizer().tokens(s)
        tokens = rename_functions(tokens)
        tokens = fixup_vector_fields(tokens)
        tokens = fixup_frame_functions(tokens)
        (self.frame_list, tokens) = fixup_macros(tokens)
        tokens = fixup_local(tokens)
        tokens = fixup_elif(tokens)
        tokens = fold_conditions(tokens)
        st = fold_compound(tokens)
        st = fixup_dowhile(st)
        (self.field_defs, st) = remove_field_defs(st)
        st = fixup_functions(st)
        (self.reset_code, st) = fixup_global_defs(st)
        self.tokens = methodize_functions(st)
        self.globals = [t.value for t in self.tokens if isinstance(t, Identifier)]    
        self.functions = [t.value for t in self.tokens if isinstance(t, Identifier) and (t.body != None) and not t.attr]    
        declare_globals(self.tokens, self.globals)
        
            
    def fix_globals(self, gdict):
        self.tokens = modularize_globals(self.basename, self.tokens, gdict, self.import_list)            

            
    def write_python(self, outfile):
        outfile.write('###\n### Generated by QuakeC -> Python translator\n### %s\n###\n' % translator_info)
        outfile.write('from qwpython.qwsv import engine, Vector\n')
        outfile.write('from qwpython.qcsupport import qc\n\n')
        for i in self.import_list:
            if not i in ['engine', 'qc']:
                outfile.write('import %s\n' % i)
        outfile.write('\n')
        
        if self.frame_list:
            outfile.write('frame = {\n') 
            for i in range(len(self.frame_list)-1):
                outfile.write("        '%s': %d,\n" % (self.frame_list[i], i))
            outfile.write("        '%s': %d\n" % (self.frame_list[-1], len(self.frame_list)-1))
            outfile.write('        }\n')

        print_structure(VectorFilter(outfile), self.tokens)
        
        if self.reset_code:
            reset_func = Identifier('qwp_reset_' + self.basename)
            reset_func.attr = []
            reset_func.body = []
            
            for i in range(len(self.reset_code)):
                if is_token(self.reset_code[i], '='):
                    reset_func.body.append(Operator('global'))
                    reset_func.body.append(self.reset_code[i-1])
                    reset_func.body.append(Semicolon())
                    
            reset_func.body += self.reset_code
            outfile.write('\n')
            print_structure(outfile, [reset_func])
            outfile.write('\n')
        
    
##############  Translate  ################################

#
# Identifiers we're going to just rename
#
rename_dict = {
        'break': 'prog_break',
        'ftos': 'str',
        'precache_sound2': 'precache_sound',
        'precache_model2': 'precache_model',
        'precache_file2': 'precache_file',
        'rint': 'round',
        'vlen': 'length',
        'vtos': 'str'
        }
        
#
# Identifiers illegal in Python that may have been used in QuakeC.
# Certainly incomplete, but it's a start.  I've definitely seen
# 'from', and 'or' used in the Deathmatch code.
#        
illegal_list = ['from', 'import', 'as', 'for', 'and', 'or', 'not', 'in', 'print']        

#
# Default values for the various QuakeC types
#
default_value = {
                 'void'     : Operator('None'),
                 'float'    : Number('0'),
                 'string'   : Operator('None'),
                 'vector'   : Vector('0 0 0'),
                 'entity'   : Identifier('engine.world')
                }

    
def rename_functions(tokens):
    identifiers = [t.value for t in tokens if isinstance(t, Identifier)]
    
    result = []
    last_line = None
    for t in tokens:
        if isinstance(t, Newline):
            # Track which line we're on just so we can print informative warnings
            last_line = t
        elif isinstance(t, Identifier):
            if rename_dict.has_key(t.value):
                t.value = rename_dict[t.value]
            elif t.value in illegal_list:
                print 'line %5d: Warning, QuakeC used Python keyword "%s" as a variable name' % (last_line.linenum, t.value)
                while t.value in identifiers:
                    t.value += '0'
                print '            will use "%s" instead' % t.value                                   
        result.append(t)
    return result


def fixup_vector_fields(tokens):
    result = []
    for t in tokens:
        if isinstance(t, Identifier) and t.value[-2:] in ['_x', '_y', '_z']:
            t.value = t.value[:-2] + '.' + t.value[-1]
        result.append(t)
    return result


def fixup_frame_functions(tokens):
    result = []
    grab_frame = 0
    frame_num = None
    nextthink = None
    for t in tokens:
        if grab_frame:
            if is_token(t, ','):
                continue
            if is_token(t, ']'):
                grab_frame = 0
            elif not frame_num:
                frame_num = t
            else:
                nextthink = t
            continue
        if is_token(t, '['):
            grab_frame = 1
            continue
        if is_token(t, '{') and frame_num:
            result.append(t)
            result.append(Identifier('self.frame'))
            result.append(Operator('='))
            result.append(frame_num)
            result.append(Semicolon())
            result.append(Identifier('self.nextthink'))
            result.append(Operator('='))
            result.append(Identifier('time'))
            result.append(Operator('+'))
            result.append(Number('0.1'))
            result.append(Semicolon())
            result.append(Identifier('self.think'))
            result.append(Operator('='))
            result.append(nextthink)
            result.append(Semicolon())
            frame_num = None
            nextthink = None
            continue
            
        result.append(t)
    return result


def fixup_macros(tokens):
    """ 
    look for tokens beginning with '$' and remove or resolve them.
    Must do this -after- fixup_frame_functions, since it will generate
    '[' and ']' tokens, which would confuse fixup_frame_functions
    """
    frame_list = []
    result = []
    skipto_newline = 0
    build_frame = 0
    for t in tokens:
        if skipto_newline:
            if isinstance(t, Newline):
                skipto_newline = 0
            continue
        if build_frame:
            if isinstance(t, Newline):
                build_frame = 0
            else:
                frame_list.append(t.value)
            continue
        if isinstance(t, Identifier) and t.value[0] == '$':
            m = t.value[1:]
            if m in ['cd', 'origin', 'base', 'flags', 'scale', 'skin']:
                skipto_newline = 1
                continue
            if m == 'frame':
                build_frame = 1
                continue

            result.append(Identifier('frame'))
            result.append(Operator('['))
            result.append(m)
            result.append(Operator(']'))
            continue

        result.append(t)                
    return (frame_list, result)


def fixup_local(tokens):
    result = []
    localref = None
    grab_next = 0
    def_value = None
    for t in tokens:
        if localref:
            if isinstance(t, Semicolon) or is_token(t, ','):
                if not have_value:
                    result.append(Operator('='))
                    result.append(def_value)
                    result.append(Semicolon(';'))                    
                if isinstance(t, Semicolon):
                    localref = None
                continue
            if is_token(t, '='):
                grab_next = 1
                continue
            if grab_next:
                result.append(Operator('='))
                result.append(t)
                result.append(Semicolon(';'))
                grab_next = 0
                have_value = 1
                continue
            if isinstance(t, Operator) and t.value in ['void', 'float', 'string', 'vector', 'entity']:
                def_value = default_value[t.value]
                continue
            localref.attr.append(t.value)
            have_value = 0
        elif is_token(t, 'local'):
            localref = t
            t.attr = []
        result.append(t)            
    return result


def fixup_elif(tokens):
    """
    merge "if else" into "elif"  on a flat list of tokens
    """
    result = []
    for t in tokens:
        if is_token(t, 'if'):
            # backtrack and see if the previous non-trivial bit was an 'else'
            for i in range(len(result)-1, -1, -1):
                t2 = result[i]
                if isinstance(t2, Newline) or isinstance(t2, Comment):
                    continue
                if is_token(t2, 'else'):
                    result = result[:i]
                    t.value = 'elif'
                break                                                
        result.append(t)
    return result    


def fold_conditions(tokens):
    """ 
    Fold the contents of tokens inside parentheses '(..)' that immediately
    follow either an identifier (indicating a function declaration or call), or
    the tokens ['if', 'elif', 'while', 'void', 'float', 'string', 'entity', 'vector']
    into a list of comma-separated lists of tokens, stored as an attribute of 
    the leading token.
    
    So for example, the QC code: "foo(a, b + c)" which was tokenized into this
    flat list of 8 tokens: 
       ['foo', '(', 'a', ',', 'b', '+', 'c', ')']
    would be folded into a single token ['foo'] that has the 'attr' attribute set to:
       [['a'], ['b', '+', 'c']]    
    """
    result = [[]]
    parenstack = [0]
    for t in tokens:
        if is_token(t, '(') and result[-1] and \
        (isinstance(result[-1][-1], Identifier) or \
        (isinstance(result[-1][-1], Operator) and \
        result[-1][-1].value in ['if', 'elif', 'while', 'void', 'float', 'string', 'entity', 'vector', '.void', '.float', '.string', '.entity', '.vector'])):
            result.append([])
            result.append([])
            parenstack.append(1)
            continue            
        if is_token(t, ',') and parenstack[-1]:
            clause = result.pop()
            result[-1].append(clause)
            result.append([]) # start a new comma-clause
            continue
        if is_token(t, ')'):
            parenstack[-1] -= 1
            if not parenstack[-1] and (len(parenstack) > 1):
                parenstack.pop()
                clause = result.pop()
                a = result.pop()
                if clause:
                    a.append(clause)
                result[-1][-1].attr = a
                
                # Special hack for the QuakeC find() function, turn 2nd param into a string
                if result[-1][-1].value == 'find':
                    a[1][0] = a[1][0].value                
                
                continue
        if is_token(t, '('):
            parenstack[-1] += 1
        result[-1].append(t)
    return result[0]        


def fold_compound(tokens):
    "Fold up compound statements delimited by '{' and '}' into sublists"
    stack = [[]]
    for t in tokens:
        if isinstance(t, Operator):
            if t.value == '{':
                stack.append([])
                continue
            elif t.value == '}':
                s = stack.pop()
                stack[-1].append(s)
                continue
        stack[-1].append(t)
    return stack[0]        


def fixup_dowhile(tokens):
    """
    turn "do ... while (cond)" into "while(1)...if not (cond): break"  
    recurses so it can run against a structured set of tokens
    """
    result = []
    found_dowhile = 0
    for t in tokens:
        if type(t) == types.ListType:
            t = fixup_dowhile(t)
        elif is_token(t, 'do'):
            t.value = 'while'
            t.attr = [[Number('1')]]
            found_dowhile = 1
        elif found_dowhile and is_token(t, 'while'):
            if t.attr[0][0].value != '1':
                t.value = 'if'    
                t.attr = [[Operator('!'), Operator('(')] + t.attr[0] + [Operator(')')]]
                result[-1].append(t)
                result[-1].append(Operator('break'))
                result[-1].append(Semicolon())
            continue
        result.append(t)
    return result
                        

def fixup_functions(tokens):
    """
    Look through the toplevel only for sequences related to 
    function definitions or declarations.  
    
    Firstly, the pattern: "type(...) identifier" is replaced with: 
    "identifier(...)" (where the (...) part is actually a list stored 
    in the .attr field of a token, as made by the fold_conditions() 
    function up above)
    
    Then the patterns for function declarations:
    
        identifier(...);
        
    and system function declarations:
    
        identifier(...) = #xxx;
        
    are dropped, leaving just the actual function definitions:
    
        identifier(...) = {...}
        
    (although this function also strips out the '=' token in this case)
    """
    result = []
    skip_to_semi = 0
    for t in tokens:
        if skip_to_semi:        
            if isinstance(t, Semicolon):
                skip_to_semi = 0
            continue
            
        if len(result) and isinstance(result[-1], Identifier) \
        and (result[-1].attr != None):
            if is_token(t, '='):
                continue
            if isinstance(t, Newline):
                continue
            if isinstance(t, Semicolon) and (result[-1].body == None):
                # Drop function declarations
                result.pop()
                continue
            if isinstance(t, Identifier) and t.value[0] == '#':
                # Drop system function definitions
                result.pop()
                skip_to_semi = 1
                continue
            if type(t) == types.ListType:
                result[-1].body = t
                continue                

        if isinstance(t, Identifier) and (t.attr == None) and \
        len(result) and isinstance(result[-1], Operator) and \
        (result[-1].attr != None):   
            t.attr = result.pop().attr
        
        result.append(t)
    return result

                        
def remove_field_defs(tokens):
    """
    Scan the toplevel and remove entity field declarations
    """
    result = []
    fields = []
    skip_tokens = 0
    for t in tokens:
        if skip_tokens:
            if isinstance(t, Semicolon):
                skip_tokens = 0
            elif isinstance(t, Identifier):
                fields.append((t.value, val))                 
            continue
        if isinstance(t, Operator) and (t.value in ['.void', '.float', '.string', '.vector', '.entity']):
            skip_tokens = 1
            val = default_value[t.value[1:]]
            continue
        result.append(t)
    return (fields, result)



system_fields = ['absmax', 'absmin', 'aiment', 'ammo_cells', 'ammo_nails', 
                 'ammo_rockets', 'ammo_shells', 'angles', 'armortype', 
                 'armorvalue', 'avelocity', 'blocked', 'button0', 'button1', 
                 'button2', 'chain', 'classname', 'colormap', 'currentammo', 
                 'deadflag', 'dmg_inflictor', 'dmg_save', 'dmg_take', 
                 'effects', 'enemy', 'fixangle', 'flags', 'frags', 'frame', 
                 'goalentity', 'gravity', 'groundentity', 'health', 'ideal_yaw', 
                 'impulse', 'items', 'lastruntime', 'ltime', 'max_health', 
                 'maxs', 'maxspeed', 'message', 'mins', 'model', 'modelindex', 'movedir', 
                 'movetype', 'netname', 'nextthink', 'noise', 'noise1', 
                 'noise2', 'noise3', 'oldorigin', 'origin', 'owner', 
                 'size', 'skin', 'solid', 'sounds', 'spawnflags', 
                 'takedamage', 'target', 'targetname', 'team', 
                 'teleport_time', 'think', 'touch', 'use', 'v_angle', 
                 'velocity', 'view_ofs', 'waterlevel', 'watertype', 
                 'weapon', 'weaponframe', 'weaponmodel', 'yaw_speed']

qcglobals = [
                ['engine',    ['ambientsound', 'bprint',  'changelevel', 'cvar', 'cvar_set', 
                               'dprint', 'lightstyle', 'multicast', 
                               'pointcontents', 'precache_sound', 'precache_model']],
                ['random',    ['random']],
                ['math',      ['ceil', 'fabs', 'floor']],
                ['qc',        ['self', 'other', 'world', 'time', 'frametime', 
                  'newmis', 'force_retouch', 'mapname', 'serverflags', 
                  'total_secrets', 'total_monsters', 'found_secrets', 
                  'killed_monsters',
                  'parm1',  'parm2',  'parm3',  'parm4',  'parm5',  'parm6',
                  'parm7',  'parm8',  'parm9',  'parm10', 'parm11', 'parm12',
                  'parm13', 'parm14', 'parm15', 'parm16',
                  'v_forward', 'v_up', 'v_right', 
                  'trace_allsolid', 'trace_startsolid', 'trace_fraction', 
                  'trace_endpos', 'trace_plane_normal', 'trace_plane_dist',
                  'trace_ent', 'trace_inopen', 'trace_inwater', 'msg_entity',
                  'end_sys_globals', 'end_sys_fields',
                  
                  'makevectors', 'setorigin', 'setmodel', 'setsize', 'break',
                  'normalize', 'error', 'objerror', 'length',
                  'vectoyaw', 'remove', 'traceline', 'checkclient',
                  'find', 'stuffcmd', 'spawn', 'stof',
                  'findradius', 'sprint', 'ftos', 'vtos',
                  'coredump', 'traceon', 'traceoff', 'eprint', 'walkmove',
                  'droptofloor', 'rint', 'sound',
                  'checkbottom', 'aim',
                  'nextent', 'ChangeYaw', 'vectoangles', 
                  'WriteByte', 'WriteChar', 'WriteShort', 'WriteLong', 
                  'WriteLong', 'WriteCoord', 'WriteAngle', 'WriteString', 
                  'WriteEntity',
                  'movetogoal', 'precache_file', 'makestatic',
                  'centerprint', 'centerprint2', 'centerprint3', 
                  'centerprint4', 'centerprint5', 'centerprint6', 
                  'centerprint7', 
                  'precache_model2', 'precache_sound2',
                  'precache_file2', 'setspawnparms', 'logfrag', 'infokey'
                  ]
                ]
            ]                  



# Make a flattened version of the above list
system_globals = []
for m in qcglobals:
    system_globals += m[1]   


def fixup_global_defs(tokens):
    result = []
    reset_code = []
    last_type = None
    has_value = 0    
    for t in tokens:
        if isinstance(t, Operator) and (t.value in ['void', 'float', 'string', 'vector', 'entity']):
            last_type = t.value
            has_value = 0
            was_system = 0
            continue
        if last_type:            
            if isinstance(t, Identifier) and (t.value in system_globals):
                was_system = 1
                has_value = 1
                continue
            if is_token(t, '='):
                has_value = 1            
            if is_token(t, ',') or is_token(t, ';'):
                if not has_value:
                    result.append(Operator('='))
                    result.append(default_value[last_type])
                    result.append(Semicolon())
                    reset_code += result[-3:]
                has_value = 0
                if is_token(t, ';'):
                    last_type = None                
                if not was_system:
                    result.append(Semicolon())
                    reset_code += result[-1:]
                was_system = 0
                continue
            reset_code.append(t)                
        result.append(t)
    return (reset_code, result)


method_functions = ['aim', 'infokey', 'length', 'logfrag', 'makestatic', 
                    'normalize', 'remove', 'setmodel', 'sound', 'sprint',
                    'stuffcmd']

def methodize_functions(tokens):    
    result = []
    last_newline = None
    for t in tokens:
        if isinstance(t, Newline):
            last_newline = t
        if type(t) == types.ListType:
           t = methodize_functions(t)
        elif isinstance(t, Identifier) or isinstance(t, Operator):
            if t.body:
                t.body = methodize_functions(t.body)   
            if t.attr:
                t.attr = methodize_functions(t.attr)
            if t.value in method_functions:
                if t.attr:
                    obj = t.attr[0]            
                    if len(obj) == 1:
                        t.attr = t.attr[1:]
                        t.value = obj[0].value + '.' + t.value            
                else:
                    if last_newline:
                        print 'Near line %d:' % last_newline.linenum,
                    print ' ERROR:', t.value, 'missing expected parameter'                        
        result.append(t)                            
    return result


def merge_lists(a, b):
    """
    Utility function used by get_global_assigns() and modularize_globals() 
    below, to merge two lists, omitting duplicates
    """
    result = a[:]
    for x in b:
        if x not in result:
            result.append(x)
    return result                    


def modularize_globals(modname, tokens, gdict, import_list, locals = None):
    """ 
    Recursively iterate through the tree, adding module
    names to variables which reside in other modules, and
    gather together a list of which modules are being 
    referred to so we can include 'import' statements
    at the top of this module.  But watch out for 
    which variables are local, and hide any globals
    of the same name.
    """
    result = []
    for t in tokens:
        if (locals == None) and isinstance(t, Identifier) and t.body:
            l2 = [a[1].value for a in t.attr]
            t.body = modularize_globals(modname, t.body, gdict, import_list, l2)
        elif type(t) == types.ListType:
            t = modularize_globals(modname, t, gdict, import_list, locals)
        elif is_token(t, 'local'):
            locals = merge_lists(locals, t.attr)
        elif isinstance(t, Identifier):
            a = string.split(t.value, '.')
            varname = a[0]            
            if ((locals != None) and (varname not in locals)) and gdict.has_key(varname):
                m = gdict[varname]
                if m != modname:                    
                    if not m in import_list:
                        import_list.append(m)
                    t.value = string.join([m] + a, '.')
            
        if (locals != None) and (not is_token(t, 'local')) and isinstance(t, QC_Token) and t.attr != None:
            t.attr = modularize_globals(modname, t.attr, gdict, import_list, locals)
        result.append(t)     
    return result



def get_global_assigns(tokens, locals, globals):
    """
    Recursively traverse a function body tree, and gather up
    a list of which globals are having values assigned to them,
    paying attention to any variables that QuakeC has declared 
    'local', which would hide any globals of the same name.
    """
    last_token = None
    result = []
    last_newline = None
    for t in tokens:
        if type(t) == types.ListType:
            result = merge_lists(result, get_global_assigns(t, locals, globals))
            continue
        if isinstance(t, Newline):
            last_newline = t
            continue
        if is_token(t, 'local'):
            for x in t.attr:
                if x in locals:
                    if last_newline:
                        print 'Near line %d:' % last_newline.linenum,
                    print " Warning, '%s' declared local, but '%s' already a local or a function param" % (x, x)
            locals = merge_lists(locals, t.attr)
        if is_token(t, '=') and (last_token.value in globals) and (last_token.value not in result):
            result.append(last_token.value)
        last_token = t
    return result                                
        
    
def declare_globals(tokens, globals):
    """
    Iterate over the toplevel only, looking for functions, and inserting
    any necessary 'global' declarations into the body of the function.
    """
    for t in tokens:
        if isinstance(t, Identifier) and t.body:
            gdefs = []
            for g in get_global_assigns(t.body, [a[1].value for a in t.attr], globals):
                gdefs.append(Operator('global'))
                gdefs.append(Identifier(g))
                gdefs.append(Semicolon())
            t.body = gdefs + t.body

###############  Print  ###########################################
            
#
# Pretty Printable Pythonized versions of QuakeC operators
#
pretty = {',': ', ', 
          '+': ' + ',
          '-': ' - ',
          '*': ' * ',
          '/': ' / ',
          '&': ' & ',
          '&&': ' and ',
          '|': ' | ',
          '||': ' or ',
          '=': ' = ',
          '==': ' == ',
          '!=': ' != ',
          '<': ' < ',
          '<=': ' <= ',
          '>': ' > ',
          '>=': ' >= ',
          '!': 'not ',
          'return': 'return ',
          'global': 'global '
         }

def print_structure(outfile, tokens, base_indent = '', allow_comments = 1):
    #
    # Recognize do-nothing blocks of code and render
    # as a Python 'pass' statement
    #
    reallist = [t for t in tokens if not (isinstance(t, Comment) or isinstance(t, Newline) or isinstance(t, Semicolon))]
    if len(reallist) == 0:
        outfile.write('pass')
        return

    need_newline = 0
    indent = base_indent
    if_stack = []
    for t in tokens:
        if is_token(t, 'local'):
            continue
            
        if isinstance(t, Newline):
            if need_newline:
                outfile.write('\n')
                outfile.write(indent)
                need_newline = 0
            continue
            
        if type(t) == types.ListType:
            if need_newline:
                outfile.write('\n')
                outfile.write(indent)
            print_structure(outfile, t, indent)
            # fall through to next if statement...
            
        if (type(t) == types.ListType) or isinstance(t, Semicolon):
            outfile.flush()
            if len(indent) > len(base_indent):
                indent = base_indent
            need_newline = 1
            continue

        if isinstance(t, Comment):
            if not allow_comments:
                continue
            if need_newline:
                outfile.write(' ')
            a = string.split(t.value, '\n')
            outfile.write('# ')
            outfile.write(a[0])
            for b in a[1:]:
                outfile.write('\n')
                outfile.write(indent)
                outfile.write('# ')
                outfile.write(b)
            if need_newline:
                outfile.write('\n')
                outfile.write(indent)
                need_newline = 0
            else:
                need_newline = 1
            outfile.flush()                
            continue

        if need_newline:
            outfile.write('\n')
            outfile.write(indent)
            need_newline = 0

        if isinstance(t, Operator) and t.value in ['if', 'elif', 'else', 'while']:
            #
            # this next bit is to ensure that 'else' and 'elif' statements are indented
            # to match the most recent 'if'
            if t.value == 'else' or t.value == 'elif':
                else_indent = if_stack.pop()
                outfile.write(' ' * (len(else_indent) - len(indent)))
                indent = else_indent
            if t.value == 'if' or t.value == 'elif':
                if_stack.append(indent)
                
            outfile.write(t.value)
            if t.attr:
                outfile.write(' ')
                print_structure(outfile, t.attr[0], indent, allow_comments=0)
            outfile.write(':')
            outfile.flush()
            indent += '    '
            need_newline = 1
            continue

        if isinstance(t, Identifier) and (t.attr != None) and (t.body != None):
            outfile.write('\ndef ')
            outfile.write(t.value)
            outfile.write('(')
            if t.attr:
                for clause in t.attr:
                    outfile.write(`clause[1]`)
                    outfile.write(', ')
            outfile.write('*qwp_extra):\n    ')
            outfile.flush()
            outfile.write(indent)
            print_structure(outfile, t.body, indent + '    ')
            need_newline = 1
            continue

        if isinstance(t, Operator) and pretty.has_key(t.value):
            outfile.write(pretty[t.value])            
            continue
            
        # Tiny hack to convert empty strings to the Python 'None' value            
        if t == '':
            t = Identifier('None') 

        # Make sure an integer isn't so big it can't be parsed in Python.
        # (to work around a bit in CTF that uses the decimal integer
        # 2147483648, which Python considers too large for an Integer,
        # but accepts if written as the hex value 0x80000000)               
        if isinstance(t, Number) and ('.' not in t.value):
            try:
                ival = int(t.value)
                outfile.write(t.value)
            except:
                ival = hex(long(t.value))[:-1]
                if len(ival) <= 10:
                    outfile.write(ival)
                else:
                    print 'Warning, integer %s is too large for Python, rewriting as a long'
                    outfile.write(t.value)
                    outfile.write('L')
            continue                    
                                                                   
        outfile.write(`t`)
        
        if isinstance(t, Identifier) and (t.attr != None):
            outfile.write('(')
            if t.attr:
                for clause in t.attr[:-1]:
                    print_structure(outfile, clause, indent)
                    outfile.write(', ')
                print_structure(outfile, t.attr[-1], indent)                    
            outfile.write(')')

##################  Actually do the work  ################################################

def translate_game():
    import sys
    if len(sys.argv) < 2:
        print 'Usage: %s <qcfile-or-dir> [<output-dir>]' % sys.argv[0]
        sys.exit()
   
    source_dir = sys.argv[1]
    if len(sys.argv) > 2:
        target_dir = sys.argv[2]
    else:
        target_dir = source_dir

    if source_dir[-3:] == '.qc':
        # Test translation of a single file to stdout
        qcfile = open(source_dir, 'r').read()
        m = QC_Module(qcfile, 'foo')
        m.write_python(sys.stdout)
        sys.exit()

    try:
        os.makedirs(target_dir)
    except:
        pass
            
    # 
    # Get the list of source files
    #
    source = open(os.path.join(source_dir, 'progs.src'), 'r').read()
    source = re.sub('//.*', '', source)     # strip out // comments
    source = re.findall('\S+', source)[1:]  # get a list of all whitespace-separated tokens, skipping the first

    modules = {}

    #
    # open, read, and create module objects from each source file
    #
    for s in source:
        filename = string.lower(string.split(os.path.split(s)[-1], '.')[0])
        if modules.has_key(filename):
            raise Exception, 'two QuakeC modules with the same base name: ' + filename
            
        print 'Reading:', s
        qcfile = open(os.path.join(source_dir, s), 'r').read()
        modules[filename] = QC_Module(qcfile, filename)
    
    #
    # Figure out which globals and global functions are in which modules
    #
    global_dict = {}
    for m in modules.values():
        for g in m.globals:
            global_dict[g] = m.basename
            
    # A few functions are actually in standard Python or QWPython modules  
    for m in qcglobals:
        for f in m[1]:
            global_dict[f] = m[0]          
            
    #
    # Go through each module and prefix identifiers with 
    # the name of the module they reside in, and write out
    # as Python code
    #
    for m in modules.values():
        print 'Writing:', m.basename + '.py'
        outfile = open(os.path.join(target_dir, m.basename + '.py'), 'w')
        m.fix_globals(global_dict)                
        m.write_python(outfile)
        
    #
    # Write out a module that joins everything together
    #        
    print 'Writing game package module: __init__.py'
    outfile = open(os.path.join(target_dir, '__init__.py'), 'w')
    outfile.write("""#
# QWPython Game translated from QuakeC Source
#
import sys
from qwpython.qwsv import engine, Vector
import qwpython.qcsupport
from qwpython.qcsupport import qc

# Stop on CTRL-C
import signal
signal.signal(signal.SIGINT, engine.stop)

#
# Modules translated from QuakeC
#
""")
    ar = modules.keys()
    ar.sort()
    for m in ar:
        outfile.write('from %s import *\n' % m)

    outfile.write("""
#
# Reset the globals that appear in the game, and
# spawn the entities specified by the map
#    
def qwp_reset():
""")
    for m in ar:
        if modules[m].reset_code:
            outfile.write('    qwp_reset_%s()\n' % m)

    outfile.write(""" 
#
# Let the engine know who to call when it's time to reset and spawn
#    
engine.reset_game = qwp_reset
engine.spawn_func = qwpython.qcsupport.spawn_entities

#
# Entity fields defined for this game
#
qwpython.qcsupport.game_entity_fields = (
""")

    ef = []
    for m in modules.values():
        for f in m.field_defs:
            if f[0] not in system_fields:
                ef.append(f)
    if ef:                
        ef.sort()
        for f in ef[:-1]:                        
            outfile.write("    ('%s', %s),\n" % f)
        outfile.write("    ('%s', %s)\n" % ef[-1])        
            
    outfile.write(""")
    
def spawn_entity(ent_class):
    sys.modules[__name__].__dict__[ent_class]()

def wrap_client_connect():
    for f in qwpython.qcsupport.game_entity_fields:  
        setattr(qc.self, f[0], f[1])
    ClientConnect()
    
def wrap_put_client_in_server():
    for f in qwpython.qcsupport.game_entity_fields: 
        if not hasattr(qc.self, f[0]): 
            setattr(qc.self, f[0], f[1])
    PutClientInServer()
    
#
# Hook up the Engine to various Python functions that it will need to call
#    
qwpython.qcsupport.spawn_func    = spawn_entity
qc.start_frame          = StartFrame
qc.player_pre_think     = PlayerPreThink
qc.player_post_think    = PlayerPostThink
qc.client_kill          = ClientKill
qc.client_connect       = wrap_client_connect
qc.put_client_in_server = wrap_put_client_in_server
qc.client_disconnect    = ClientDisconnect
qc.set_new_parms        = SetNewParms
qc.set_change_parms     = SetChangeParms

#
# Run the game
#
engine.run()
""")

###### Main #################

if __name__ == '__main__':
    translate_game()
            
########### EOF ##################


