#ifndef KRATOS_EVENT_HH
#define KRATOS_EVENT_HH

#include "stmt.hh"

namespace kratos {

class Event {
public:
    explicit Event(std::string event_name) : event_name_(std::move(event_name)) {}
    std::shared_ptr<EventTracingStmt> fire(
        const std::map<std::string, std::shared_ptr<Var>> &fields);

private:
    std::string event_name_;
};

// actual information used for codegen and other debug info
struct EventInfo {
    std::string name;
    std::string transaction;
    bool combinational;
    EventActionType type;
    std::shared_ptr<Var> condition;
    std::map<std::string, std::shared_ptr<Var>> fields;
};

std::vector<EventInfo> extract_event_fire_condition(Generator *top);

void remove_event_stmts(Generator *top);

}  // namespace kratos

#endif  // KRATOS_EVENT_HH
