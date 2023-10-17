import re

################################################
## Recursive Descent Monadic Parser Combinator
## (aka Seed-Grow parser)
## (for defining the parser for grammar rules)
################################################
class RDParser:

    @staticmethod
    def ignore(ignore, parse, str, mem):
        ign = ignore(str, mem)
        if not ign:
            return None
        return parse(ign[1], mem)

    @classmethod
    def str(self, strg):
        l = len(strg)
        def parse(str, mem, ignore = None):
            s = str[0:l]
            if s == strg:
                return strg, str[l:]
            elif ignore:
                return self.ignore(ignore, parse, str, mem)
            return None
        return parse

    @classmethod
    def rgx(self, regex):
        reg = re.compile(regex)
        def parse(str, mem, ignore = None):
            m = reg.match(str)
            if m != None:
                res = m.group(0)
                return res, str[len(res):]
            elif ignore:
                return self.ignore(ignore, parse, str, mem)
            return None
        return parse

    def val(val):
        def parse(str, mem, ignore = None):
            return val, str
        return parse

    @staticmethod
    def raw(_parse):
        def parse(str, mem, ignore = None):
            return _parse(str, mem)
        return parse

    ################################
    ## $ : end of stream
    ################################
    @classmethod
    def end(self):
        def parse(str, mem, ignore = None):
            if str == "":
                return None, ""
            elif ignore:
                return self.ignore(ignore, parse, str, mem)
            return None
        return parse


    ################################
    ## A B .. Z : concatenation, sequence
    ################################
    @staticmethod
    def seq(*parsers):
        def parse(str, mem, ignore = None):
            idx = 0
            seq = [None for _ in parsers]
            for parse in parsers:
                res = parse(str, mem, ignore)
                if not res:
                    return None
                seq[idx], str = res
                idx = idx + 1
            return seq, str
        return parse


    ################################
    ## A | B | ... | Z : alternation
    ################################
    @staticmethod
    def alt(*parsers):
        def parse(str, mem, ignore = None):
            for parse in parsers:
                res = parse(str, mem, ignore)
                if res:
                    return res
            return None
        return parse


    ################################
    ## A? : zero or one
    ################################
    @staticmethod
    def mbe(_parse):
        def parse(str, mem, ignore = None):
            res = _parse(str, mem, ignore)
            val = None
            if res:
                val, str = res
            return val, str
        return parse


    ################################
    ## A* : zero or more
    ################################
    @staticmethod
    def lst(_parse):
        def parse(str, mem, ignore = None):
            idx = 0
            lst = []
            res = _parse(str, mem, ignore)
            while res:
                _, str = res
                lst.append(res[0])
                idx = idx + 1
                res = _parse(str, mem, ignore)
            return lst, str
        return parse


    ################################
    ## A+ : one or more
    ################################
    @staticmethod
    def lst1(_parse):
        def parse(str, mem, ignore = None):
            idx = 0
            lst = []
            res = _parse(str, mem, ignore)
            while res:
                _, str = res
                lst.append(res[0])
                idx = idx + 1
                res = _parse(str, mem, ignore)
            return None if not idx else lst, str
        return parse


    ################################
    ## Semantics action
    ################################
    @staticmethod
    def act(_parse, act):
        def parse(str, mem, ignore = None):
            res = _parse(str, mem, ignore)
            if res:
                return act(res[0]), res[1]
            return None
        return parse

    ################################
    ## Left recursion
    ################################
    @staticmethod
    def grow(id, _parser):

        def lazy(str, mem, ignore = None):
            return ptr[0](str, mem, ignore)

        def parse(str, mem, ignore = None):
            pos = len(str)
            uid = f"{id}:{pos}"
            if uid in mem:
                return mem[uid]
            mem[uid] = None
            res = _parse(str, mem, ignore)
            while res and (not mem[uid] or len(res[1]) < len(mem[uid][1])):
                mem[uid] = res
                res = _parse(str, mem, ignore)
            return mem[uid]

        ptr = [None]
        _parse = _parser(lazy)
        ptr[0] = parse
        return parse
