cc(company).
cc(cc1).
cc(cc1_1).
cc(cc1_2).
cc(cc2).
cc(cc2_1).
cc(cc2_2).
cc_parent(cc1, company).
cc_parent(cc1_1, cc1).
cc_parent(cc1_2, cc1).
cc_parent(cc2, company).
cc_parent(cc2_1, cc2).
cc_parent(cc2_2, cc2).
org_unit(company, leadership).
org_unit(cc1, leadership).
org_unit(cc1_1, support).
org_unit(cc1_2, delivery).
org_unit(cc2, leadership).
org_unit(cc2_1, delivery).
org_unit(cc2_2, support).
emp(e000, vp, company).
emp(e001, director, cc1).
emp(e002, manager, cc1_1).
emp(e003, manager, cc1_2).
emp(e004, director, cc2).
emp(e005, manager, cc2_1).
emp(e006, manager, cc2_2).
emp(e007, analyst, cc1_1).
emp(e008, analyst, cc1_2).
emp(e009, analyst, cc1_2).
emp(e010, analyst, cc1_2).
emp(e011, analyst, cc2_1).
emp(e012, analyst, cc2_1).
emp(e013, analyst, cc2_2).
emp(e014, analyst, cc2_2).
reports(e001, e000).
reports(e002, e001).
reports(e003, e001).
reports(e004, e000).
reports(e005, e004).
reports(e006, e004).
reports(e007, e002).
reports(e008, e003).
reports(e009, e003).
reports(e010, e003).
reports(e011, e005).
reports(e012, e005).
reports(e013, e006).
reports(e014, e006).
role_limit(analyst, 5000).
role_limit(manager, 40000).
role_limit(senior_manager, 50000).
role_limit(director, 100000).
role_limit(vp, 500000).
vendor(acme, approved).
vendor(bolt, suspended).
vendor(cog, approved).
vendor(dyne, approved).
vendor(edge, approved).
vendor(fern, suspended).
req(r001, e008, 20000, hardware, fern, 20260708, pending).
req(r002, e006, 12000, services, cog, 20260803, pending).
req(r003, e004, 45000, hardware, acme, 20260827, pending).
req(r004, e014, 12000, hardware, fern, 20260712, pending).
req(r005, e014, 38000, services, acme, 20260609, pending).
req(r006, e003, 120000, hardware, bolt, 20260808, pending).
req(r007, e009, 60000, software, dyne, 20260825, pending).
req(r008, e010, 8000, software, acme, 20260826, pending).
req(r009, e009, 38000, services, fern, 20260731, pending).
req(r010, e014, 60000, capital, cog, 20260625, pending).
req(r011, e013, 3000, software, fern, 20260619, pending).
req(r012, e009, 45000, capital, cog, 20260818, pending).
req(r013, e014, 120000, services, cog, 20260901, pending).
req(r014, e004, 90000, hardware, bolt, 20260722, pending).
req(r015, e009, 20000, software, fern, 20260627, cancelled).
req(r016, e009, 20000, hardware, bolt, 20260601, pending).
req(r017, e007, 38000, software, fern, 20260825, pending).
req(r018, e013, 90000, capital, fern, 20260829, pending).
emergency(r002).
emergency(r004).
emergency(r011).
emergency(r015).
emergency(r018).
violation(e010).
booked(cc1_1, 112000).
booked(cc1_2, 83000).
booked(cc2_1, 93000).
booked(cc2_2, 43000).
cap(company, 397000).
cap(cc1, 292000).
cap(cc1_1, 134000).
cap(cc1_2, 116000).
cap(cc2, 156000).
cap(cc2_1, 95000).
cap(cc2_2, 47000).
today(20260915).
role_limit_version(analyst, 5000, 20260101, 20261231).
role_limit_version(manager, 25000, 20260101, 20260731).
role_limit_version(manager, 40000, 20260801, 20261231).
role_limit_version(senior_manager, 50000, 20260101, 20261231).
role_limit_version(director, 100000, 20260101, 20261231).
role_limit_version(vp, 500000, 20260101, 20261231).
vendor_status(acme, approved, 20260101, 20261231).
vendor_status(bolt, approved, 20260101, 20260731).
vendor_status(bolt, suspended, 20260801, 20261231).
vendor_status(cog, approved, 20260101, 20261231).
vendor_status(dyne, suspended, 20260101, 20260630).
vendor_status(dyne, approved, 20260701, 20261231).
vendor_status(edge, approved, 20260101, 20261231).
vendor_status(fern, suspended, 20260101, 20261231).
assignment(e000, company, finance, 20260101).
assignment(e000, company, hr, 20260101).
assignment(e001, cc1, finance, 20260101).
assignment(e001, cc1, hr, 20260101).
assignment(e002, cc1_1, finance, 20260101).
assignment(e002, cc1_1, hr, 20260101).
assignment(e003, cc1_2, finance, 20260101).
assignment(e003, cc1_2, hr, 20260101).
assignment(e004, cc2, finance, 20260101).
assignment(e004, cc2, hr, 20260101).
assignment(e005, cc2_1, finance, 20260101).
assignment(e005, cc2_1, hr, 20260101).
assignment(e006, cc2_2, finance, 20260101).
assignment(e006, cc2_2, hr, 20260101).
assignment(e007, cc1_1, finance, 20260101).
assignment(e007, cc1_1, hr, 20260101).
assignment(e008, cc1_1, finance, 20260101).
assignment(e008, cc1_2, finance, 20260907).
assignment(e008, cc1_1, hr, 20260101).
assignment(e008, cc1_2, hr, 20260805).
assignment(e009, cc1_2, finance, 20260101).
assignment(e009, cc1_2, hr, 20260101).
assignment(e010, cc1_2, finance, 20260101).
assignment(e010, cc1_2, hr, 20260101).
assignment(e011, cc2_1, finance, 20260101).
assignment(e011, cc2_1, hr, 20260101).
assignment(e011, cc1_1, hr, 20260826).
assignment(e012, cc2_1, finance, 20260101).
assignment(e012, cc2_1, hr, 20260101).
assignment(e013, cc2_2, finance, 20260101).
assignment(e013, cc2_2, hr, 20260101).
assignment(e014, cc2_2, finance, 20260101).
assignment(e014, cc2_2, hr, 20260101).
exemption(capex, capital, 20260101).
exemption_withdrawn(capex, 20260810).
