import enum
from .pyast import transform_stmt_block, get_fn_ln
import _kratos
from typing import List, Dict

__GLOBAL_DEBUG = False


def set_global_debug(value: bool):
    global __GLOBAL_DEBUG
    assert isinstance(value, bool)
    __GLOBAL_DEBUG = value


def get_global_debug():
    return __GLOBAL_DEBUG


# this is a wrapper python class to interface with the underlying python
# binding
class PortDirection(enum.Enum):
    In = _kratos.PortDirection.In
    Out = _kratos.PortDirection.Out
    InOut = _kratos.PortDirection.InOut


class PortType(enum.Enum):
    Data = _kratos.PortType.Data
    Clock = _kratos.PortType.Clock
    AsyncReset = _kratos.PortType.AsyncReset
    ClockEnable = _kratos.PortType.ClockEnable
    Reset = _kratos.PortType.Reset


class BlockEdgeType(enum.Enum):
    Posedge = _kratos.BlockEdgeType.Posedge
    Negedge = _kratos.BlockEdgeType.Negedge


class StatementBlockType(enum.Enum):
    Combinational = _kratos.StatementBlockType.Combinational
    Sequential = _kratos.StatementBlockType.Sequential


class CodeBlock:
    # this is a magic number
    FRAME_DEPTH = 4

    def __init__(self, generator: "Generator", block_type: StatementBlockType):
        self.block_type = block_type
        self._generator = generator
        if block_type == StatementBlockType.Combinational:
            self._block = generator.internal_generator.combinational()
        else:
            self._block = generator.internal_generator.sequential()

        if generator.debug:
            fn, ln = get_fn_ln(CodeBlock.FRAME_DEPTH)
            self._block.add_fn_ln((fn, ln))

    def add_stmt(self, stmt):
        if hasattr(stmt, "stmt"):
            self._block.add_statement(stmt.stmt())
        else:
            self._block.add_statement(stmt)

    def stmt(self):
        return self._block


class SequentialCodeBlock(CodeBlock):
    def __init__(self, generator: "Generator", sensitivity_list):
        super().__init__(generator, StatementBlockType.Sequential)
        for cond, var in sensitivity_list:
            assert isinstance(cond, BlockEdgeType)
            assert isinstance(var, _kratos.Var)
            self._block.add_condition([cond.value, var])


class CombinationalCodeBlock(CodeBlock):
    def __init__(self, generator: "Generator"):
        super().__init__(generator, StatementBlockType.Combinational)


class PortProxy:
    def __init__(self, generator: "Generator"):
        self.__generator = generator

    def __getitem__(self, key):
        return self.__generator.internal_generator.get_port(key)

    def __getattr__(self, key):
        return self.__generator.internal_generator.get_port(key)


class GeneratorMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._cache = {}


class Generator(metaclass=GeneratorMeta):
    __context = _kratos.Context()
    __inspect_frame_depth: int = 2

    def __init__(self, name: str, debug: bool = False,
                 ):
        self.__generator = self.__context.generator(name)
        self.__child_generator: Dict[str, Generator] = {}

        if not debug:
            self.debug = get_global_debug()
        else:
            self.debug = debug

        if debug:
            fn, ln = get_fn_ln(Generator.__inspect_frame_depth)
            self.__generator.add_fn_ln((fn, ln))

        # gemstone style port interface
        self.ports = PortProxy(self)

    def __getitem__(self, instance_name: str):
        assert instance_name in self.__child_generator, \
            "{0} does not exist in {1}".format(instance_name,
                                               self.instance_name)
        return self.__child_generator[instance_name]

    def __setitem__(self, instance_name: str, generator: "Generator"):
        if instance_name in self.__child_generator:
            raise Exception(
                "{0} already exists in {1}".format(self.instance_name,
                                                   self.instance_name))
        assert isinstance(generator,
                          Generator), "generator is not a Generator instance"

        self.__child_generator[instance_name] = generator
        self.__generator.add_child_generator(generator.__generator,
                                             False)

    @property
    def name(self):
        return self.__generator.name

    @name.setter
    def name(self, name: str):
        self.__generator.name = name

    @property
    def instance_name(self):
        return self.__generator.name

    @instance_name.setter
    def instance_name(self, name: str):
        self.__generator.instance_name = name

    @property
    def is_stub(self):
        return self.__generator.is_stub()

    @is_stub.setter
    def is_stub(self, value: bool):
        self.__generator.set_is_stub(value)

    @property
    def external(self):
        return self.__generator.external()

    @external.setter
    def external(self, value: bool):
        self.__generator.set_external(value)

    @property
    def debug(self):
        return self.__generator.debug

    @debug.setter
    def debug(self, value):
        self.__generator.debug = value

    @property
    def is_cloned(self):
        return self.__generator.is_cloned()

    def var(self, name: str, width: int,
            is_signed: bool = False) -> _kratos.Var:
        v = self.__generator.var(name, width, is_signed)
        if self.debug:
            fn, ln = get_fn_ln()
            v.add_fn_ln((fn, ln))
        return v

    def port(self, name: str, width: int, direction: PortDirection,
             port_type: PortType = PortType.Data,
             is_signed: bool = False) -> _kratos.Port:
        p = self.__generator.port(direction.value, name, width,
                                  port_type.value, is_signed)
        if self.debug:
            fn, ln = get_fn_ln()
            p.add_fn_ln((fn, ln))
        return p

    def port_packed(self, name: str, direction: PortDirection,
                    struct_packed: _kratos.PortPacked):
        p = self.__generator.port_packed(direction.value, name,
                                         struct_packed)
        if self.debug:
            fn, ln = get_fn_ln()
            p.add_fn_ln((fn, ln))
        return p

    def parameter(self, name: str, width: int,
                  is_signed: bool = False) -> _kratos.Param:
        param = self.__generator.parameter(name, width, is_signed)

        if self.debug:
            fn, ln = get_fn_ln()
            param.add_fn_ln((fn, ln))
        return param

    def get_var(self, name):
        return self.__generator.get_var(name)

    def const(self, value: int, width: int, signed: bool = False):
        return self.__generator.constant(value, width, signed)

    @property
    def internal_generator(self):
        return self.__generator

    def add_code(self, fn):
        raw_sensitives, stmts = transform_stmt_block(self, fn, self.debug)
        if len(raw_sensitives) == 0:
            # it's a combinational block
            comb = CombinationalCodeBlock(self)
            for stmt in stmts:
                comb.add_stmt(stmt)
        else:
            sensitivity_list = []
            for edge, var_name in raw_sensitives:
                edge = BlockEdgeType[edge]
                var = self.internal_generator.get_var(var_name)
                sensitivity_list.append((edge, var))
            seq = SequentialCodeBlock(self, sensitivity_list)
            for stmt in stmts:
                seq.add_stmt(stmt)

    def __assign(self, var_from, var_to):
        stmt = var_from.assign(var_to, _kratos.AssignmentType.Blocking)
        self.add_stmt(stmt)
        return stmt

    def wire(self, var_to, var_from):
        # this is a top level direct wire assignment
        # notice that we can figure out the direction automatically if
        # both of them are ports
        if isinstance(var_to, _kratos.Port) and isinstance(var_from,
                                                           _kratos.Port):
            stmt = self.__generator.wire_ports(var_to, var_from)
        else:
            stmt = self.__assign(var_to, var_from)

        if self.debug:
            fn, ln = get_fn_ln(2)
            stmt.add_fn_ln((fn, ln))

    def add_stmt(self, stmt):
        self.__generator.add_stmt(stmt)

    def add_child_generator(self, instance_name: str, generator: "Generator"):
        generator.instance_name = instance_name
        self[instance_name] = generator

    @staticmethod
    def clear_context():
        Generator.__context.clear()
        # also clean the caches
        clses = Generator.__subclasses__()
        for cls in clses:   # type: Generator
            cls._cache.clear()

    @staticmethod
    def get_context():
        return Generator.__context

    @staticmethod
    def from_verilog(top_name: str, src_file: str, lib_files: List[str],
                     port_mapping: Dict[str, PortType]):
        g = Generator("")
        _port_mapping = {}
        for name, _type in port_mapping.items():
            _port_mapping[name] = _type.value
        g.__generator = _kratos.Generator.from_verilog(Generator.__context,
                                                       src_file, top_name,
                                                       lib_files, _port_mapping)
        Generator.__context.add(g.__generator)
        return g

    def __contains__(self, generator: "Generator"):
        if not isinstance(generator, (Generator, _kratos.Generator)):
            return False
        elif isinstance(generator, Generator):
            return self.__generator.has_child_generator(generator.__generator)
        else:
            return self.__generator.has_child_generator(generator)

    def clone(self, copy_port_attr: bool = True):
        g = Generator("")
        g.__generator = self.__generator.clone()
        if copy_port_attr:
            # copy all the port attributes over
            attributes = self.__dict__
            for name, value in attributes.items():
                if isinstance(value, _kratos.Port):
                    setattr(g, name, g.__generator.get_port(value.name))
        return g

    @classmethod
    def create(cls, **kargs):
        # compute the hash
        hash_value = 0
        for key, value in kargs.items():
            hash_value = hash_value ^ (hash(key) << 16) ^ hash(value)
        if hash_value not in cls._cache:
            g = cls(**kargs)
            cls._cache[hash_value] = g
            return g
        else:
            g = cls._cache[hash_value]
            return g.clone()


def always(sensitivity):
    for edge, var in sensitivity:
        assert isinstance(edge, BlockEdgeType)
        assert isinstance(var, str)

    def wrapper(fn):
        return fn

    return wrapper


def signed(var):
    assert isinstance(var, _kratos.Var)
    return var.signed_()


def verilog(generator: Generator, optimize_if: bool = True,
            optimize_passthrough: bool = True,
            optimize_fanout: bool = True,
            debug=False,
            additional_passes=None,
            extra_struct=False):
    code_gen = _kratos.VerilogModule(generator.internal_generator)
    pass_manager = code_gen.pass_manager()
    if additional_passes is not None:
        for name, fn in additional_passes.items():
            pass_manager.add_pass(name, fn)
    code_gen.run_passes(optimize_if, optimize_passthrough, optimize_fanout)
    src = code_gen.verilog_src()
    result = [src]
    if debug:
        info = _kratos.passes.extract_debug_info(generator.internal_generator)
        result.append(info)

    if extra_struct:
        strct_info = _kratos.passes.extract_struct_info(
            generator.internal_generator)
        result.append(strct_info)

    return result[0] if len(result) == 1 else result
