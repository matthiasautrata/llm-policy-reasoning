
CREATE TABLE cc (
	id TEXT NOT NULL,
	parent TEXT,
	level INTEGER NOT NULL,
	org_unit TEXT NOT NULL,
	booked INTEGER NOT NULL,
	cap INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX ix_cc_id ON cc (id);
COMMENT ON TABLE cc IS 'A cost centre: a node of the budget tree, with its spending cap and the spend booked directly on it this quarter.';
COMMENT ON COLUMN cc.id IS 'Cost centre id.';
COMMENT ON COLUMN cc.parent IS 'Parent cost centre; empty for the root.';
COMMENT ON COLUMN cc.level IS 'Depth in the tree; the root is 0.';
COMMENT ON COLUMN cc.org_unit IS 'Organisational unit the centre belongs to.';
COMMENT ON COLUMN cc.booked IS 'Spend booked directly on this centre (not its descendants).';
COMMENT ON COLUMN cc.cap IS 'Spending cap of the centre this quarter.';

CREATE TABLE emp (
	id TEXT NOT NULL,
	role TEXT NOT NULL,
	cc TEXT NOT NULL,
	manager TEXT,
	violation BOOLEAN NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX ix_emp_id ON emp (id);
COMMENT ON TABLE emp IS 'An employee, their role, their cost centre as finance records it, and their direct manager.';
COMMENT ON COLUMN emp.id IS 'Employee id.';
COMMENT ON COLUMN emp.role IS 'Role; governs the approval limit.';
COMMENT ON COLUMN emp.cc IS 'Current cost centre in the finance system.';
COMMENT ON COLUMN emp.manager IS 'Direct manager; empty for the vp.';
COMMENT ON COLUMN emp.violation IS 'The employee has a recorded policy violation.';

CREATE TABLE req (
	id TEXT NOT NULL,
	requester TEXT NOT NULL,
	amount INTEGER NOT NULL,
	category TEXT NOT NULL,
	vendor TEXT NOT NULL,
	date DATE NOT NULL,
	status TEXT NOT NULL,
	emergency BOOLEAN NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX ix_req_id ON req (id);
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
	emp TEXT NOT NULL,
	cc TEXT NOT NULL,
	source TEXT NOT NULL,
	effective DATE NOT NULL,
	UNIQUE (emp, source, effective)
);
CREATE INDEX assignment_emp_source_effective_idx ON assignment (emp, source, effective);
COMMENT ON TABLE assignment IS 'A source''s record (hr or finance) that an employee belongs to a cost centre from the effective date on.';
COMMENT ON COLUMN assignment.emp IS 'Employee.';
COMMENT ON COLUMN assignment.cc IS 'Cost centre.';
COMMENT ON COLUMN assignment.source IS 'hr or finance.';
COMMENT ON COLUMN assignment.effective IS 'Effective from.';

CREATE TABLE role_limit_version (
	role TEXT NOT NULL,
	"limit" INTEGER NOT NULL,
	valid_from DATE NOT NULL,
	valid_to DATE NOT NULL,
	UNIQUE (role, valid_from)
);
CREATE INDEX role_limit_version_role_valid_from_idx ON role_limit_version (role, valid_from);
COMMENT ON TABLE role_limit_version IS 'A dated version of a role''s approval limit, valid from and to the given dates inclusive.';
COMMENT ON COLUMN role_limit_version.role IS 'Role.';
COMMENT ON COLUMN role_limit_version."limit" IS 'Approval limit.';
COMMENT ON COLUMN role_limit_version.valid_from IS 'First day valid.';
COMMENT ON COLUMN role_limit_version.valid_to IS 'Last day valid.';

CREATE TABLE vendor_status (
	vendor TEXT NOT NULL,
	status TEXT NOT NULL,
	valid_from DATE NOT NULL,
	valid_to DATE NOT NULL,
	UNIQUE (vendor, valid_from)
);
CREATE INDEX vendor_status_vendor_valid_from_idx ON vendor_status (vendor, valid_from);
COMMENT ON TABLE vendor_status IS 'A vendor''s status during a period, from and to the given dates inclusive.';
COMMENT ON COLUMN vendor_status.vendor IS 'Vendor.';
COMMENT ON COLUMN vendor_status.status IS 'approved or suspended.';
COMMENT ON COLUMN vendor_status.valid_from IS 'First day.';
COMMENT ON COLUMN vendor_status.valid_to IS 'Last day.';

