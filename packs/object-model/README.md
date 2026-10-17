# ObjectModel 0.1

Create a live caller-owned instance with an explicit type contract, initialized field IDs and actual CLR values. Omitted fields remain unset. Read and Write validate the field contract and actual instance type. Create allocates a distinct instance and stores the supplied values directly; arrays and object references are retained without deep copying. No declaration-data hydration, implicit defaults, global instance registry, owner transfer, serialization of live references or lifetime manager is provided.

The object[] state returned as object is an opaque implementation detail; consumers pass it through ordinary object contracts. Typed Blueprint property reads use Read once at the execution node, then retain the result slot. Projects can explicitly bind a compatible Read provider to adapt their own live CLR model. This does not change Blueprint timing or make the implementation's C# this an object receiver.
