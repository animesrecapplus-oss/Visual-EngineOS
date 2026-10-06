# Relations

`REL-SPC-001`: `state_policy → state_policy_contract` — canonical value-contract dependency.
`REL-SPC-002`: `consequence_bindings → state_policy_contract` — typed state activation consumption.
`REL-SPC-003`: `resolution_context → state_policy_contract` — typed context-state consumption.
`REL-SPC-004`: `runtime.__init__ → state_policy → state_policy_contract` — preserved public API through compatibility facade.
`REL-SPC-005`: `state_policy` remains a compatibility facade over the canonical value owner.
