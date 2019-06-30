#ifndef KRATOS_CODEGEN_H
#define KRATOS_CODEGEN_H

#include "context.hh"
#include "ast.hh"
#include <sstream>

class VerilogModule {
public:
    explicit VerilogModule(Generator *generator);

    const std::map<std::string, std::string> &verilog_src() const { return verilog_src_; }

private:
    std::map<std::string, std::string> verilog_src_;
};


class SystemVerilogCodeGen {
public:
    explicit SystemVerilogCodeGen(Generator *generator);
    const std::string str() { return stream_.str(); }

    uint32_t indent_size = 2;

private:
    uint32_t indent_ = 0;
    std::stringstream stream_;
    Generator* generator_;

    static std::string get_var_width_str(const Var *var);
    void generate_ports(Generator* generator);
    void generate_variables(Generator* generator);
    std::string get_port_str(Port* port);

    std::string indent();

    std::string dispatch_str(ASTNode* node);

    std::string to_string(AssignStmt* stmt);

    std::string to_string(StmtBlock* stmt);

    std::string to_string(SequentialStmtBlock* stmt);

    std::string to_string(CombinationalStmtBlock* stmt);

    std::string to_string(IfStmt* stmt);

    std::string to_string(ModuleInstantiationStmt* stmt);

    template <typename Iter>
    std::string join(Iter begin, Iter end, const std::string& sep) {
        std::stringstream stream;
        for (auto it = begin; it != end; it++) {
            if (it != begin) stream << sep;
            stream << *it;
        }
        return stream.str();
    }
};

#endif  //KRATOS_CODEGEN_H
