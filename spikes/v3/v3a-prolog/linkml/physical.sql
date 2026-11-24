
CREATE TABLE cc (
	id TEXT,
	parent TEXT,
	level INTEGER,
	org_unit TEXT,
	booked INTEGER,
	cap INTEGER
);
COMMENT ON TABLE cc IS 'A cost centre: a node of the budget tree, with its spending cap and the spend booked directly on it this quarter.';
COMMENT ON COLUMN cc.id IS 'Cost centre id.';
COMMENT ON COLUMN cc.parent IS 'Parent cost centre; empty for the root.';
COMMENT ON COLUMN cc.level IS 'Depth in the tree; the root is 0.';
COMMENT ON COLUMN cc.org_unit IS 'Organisational unit the centre belongs to.';
COMMENT ON COLUMN cc.booked IS 'Spend booked directly on this centre (not its descendants).';
COMMENT ON COLUMN cc.cap IS 'Spending cap of the centre this quarter.';

CREATE TABLE emp (
	id TEXT,
	role TEXT,
	cc TEXT,
	manager TEXT,
	violation BOOLEAN
);
COMMENT ON TABLE emp IS 'An employee, their role, their cost centre as finance records it, and their direct manager.';
COMMENT ON COLUMN emp.id IS 'Employee id.';
COMMENT ON COLUMN emp.role IS 'Role; governs the approval limit.';
COMMENT ON COLUMN emp.cc IS 'Current cost centre in the finance system.';
COMMENT ON COLUMN emp.manager IS 'Direct manager; empty for the vp.';
COMMENT ON COLUMN emp.violation IS 'The employee has a recorded policy violation.';

CREATE TABLE req (
	id TEXT,
	requester TEXT,
	amount INTEGER,
	category TEXT,
	vendor TEXT,
	date DATE,
	status TEXT,
	emergency BOOLEAN
);
COMMENT ON TABLE req IS 'A purchase request, raised on a date by an employee, for an amount, category and vendor.';
COMMENT ON COLUMN req.id IS 'Request id.';
COMMENT ON COLUMN req.requester IS 'Employee who raised the request.';
COMMENT ON COLUMN req.amount IS 'Amount requested.';
COMMENT ON COLUMN req.category IS 'Spend category (code list codes:category).';
COMMENT ON COLUMN req.vendor IS 'Vendor the purchase is from.';
COMMENT ON COLUMN req.date IS 'Date the request was raised; governs dated rules (R203).';
COMMENT ON COLUMN req.status IS 'pending or cancelled.';
COMMENT ON COLUMN req.emergency IS 'Flagged as an emergency.';

CREATE TABLE assignment (
	emp TEXT,
	cc TEXT,
	source TEXT,
	effective DATE
);
COMMENT ON TABLE assignment IS 'A source''s record (hr or finance) that an employee belongs to a cost centre from the effective date on.';
COMMENT ON COLUMN assignment.emp IS 'Employee.';
COMMENT ON COLUMN assignment.cc IS 'Cost centre.';
COMMENT ON COLUMN assignment.source IS 'hr or finance.';
COMMENT ON COLUMN assignment.effective IS 'Effective from.';

CREATE TABLE role_limit_version (
	role TEXT,
	"limit" INTEGER,
	valid_from DATE,
	valid_to DATE
);
COMMENT ON TABLE role_limit_version IS 'A dated version of a role''s approval limit, valid from and to the given dates inclusive.';
COMMENT ON COLUMN role_limit_version.role IS 'Role.';
COMMENT ON COLUMN role_limit_version."limit" IS 'Approval limit.';
COMMENT ON COLUMN role_limit_version.valid_from IS 'First day valid.';
COMMENT ON COLUMN role_limit_version.valid_to IS 'Last day valid.';

CREATE TABLE vendor_status (
	vendor TEXT,
	status TEXT,
	valid_from DATE,
	valid_to DATE
);
COMMENT ON TABLE vendor_status IS 'A vendor''s status during a period, from and to the given dates inclusive.';
COMMENT ON COLUMN vendor_status.vendor IS 'Vendor.';
COMMENT ON COLUMN vendor_status.status IS 'approved or suspended.';
COMMENT ON COLUMN vendor_status.valid_from IS 'First day.';
COMMENT ON COLUMN vendor_status.valid_to IS 'Last day.';

