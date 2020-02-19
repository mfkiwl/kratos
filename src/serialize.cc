#include "serialize.hh"

#include <cereal/archives/json.hpp>
#include <cereal/archives/binary.hpp>
#include <cereal/types/polymorphic.hpp>

// register base types
CEREAL_REGISTER_TYPE(kratos::IRNode)   // NOLINT
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::IRNode, kratos::Generator)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::IRNode, kratos::Var)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::Expr)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::Const)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::VarSlice)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::VarCasted)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::VarSlice, kratos::VarVarSlice)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Const, kratos::Param)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::VarSlice, kratos::PackedSlice)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::VarPackedStruct)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Expr, kratos::VarConcat)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Expr, kratos::VarExtend)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Expr, kratos::ConditionalExpr)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Const, kratos::EnumConst)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::EnumVar)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::FunctionCallVar)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::InterfaceVar)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Var, kratos::Port)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Port, kratos::EnumPort)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Port, kratos::PortPackedStruct)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::Port, kratos::InterfacePort)
CEREAL_REGISTER_POLYMORPHIC_RELATION(kratos::InterfacePort, kratos::ModportPort)

namespace kratos {

void serialize(std::ostream &ostream, std::shared_ptr<Context> context) {
    cereal::JSONOutputArchive o_archive(ostream);
    o_archive(context);
}
}