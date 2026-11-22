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
org_unit(cc1_2, support).
org_unit(cc2, leadership).
org_unit(cc2_1, support).
org_unit(cc2_2, delivery).
emp(e000, vp, company).
emp(e001, director, cc1).
emp(e002, manager, cc1_1).
emp(e003, manager, cc1_2).
emp(e004, director, cc2).
emp(e005, manager, cc2_1).
emp(e006, manager, cc2_2).
emp(e007, analyst, cc1_1).
emp(e008, analyst, cc1_1).
emp(e009, analyst, cc1_2).
emp(e010, analyst, cc1_2).
emp(e011, analyst, cc2_1).
emp(e012, analyst, cc2_2).
emp(e013, analyst, cc2_2).
emp(e014, analyst, cc2_2).
reports(e001, e000).
reports(e002, e001).
reports(e003, e001).
reports(e004, e000).
reports(e005, e004).
reports(e006, e004).
reports(e007, e002).
reports(e008, e002).
reports(e009, e003).
reports(e010, e003).
reports(e011, e005).
reports(e012, e006).
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
req(r001, e013, 38000, hardware, cog, 20260617, pending).
req(r002, e008, 8000, software, edge, 20260724, cancelled).
req(r003, e010, 38000, services, acme, 20260617, pending).
req(r004, e011, 60000, capital, cog, 20260624, pending).
req(r005, e002, 12000, software, dyne, 20260907, pending).
req(r006, e005, 12000, software, bolt, 20260818, pending).
req(r007, e009, 8000, software, acme, 20260620, pending).
req(r008, e011, 12000, hardware, fern, 20260612, pending).
req(r009, e005, 3000, hardware, fern, 20260727, pending).
req(r010, e014, 90000, capital, fern, 20260719, pending).
req(r011, e003, 3000, capital, fern, 20260604, pending).
req(r012, e009, 120000, software, dyne, 20260831, pending).
req(r013, e007, 60000, hardware, fern, 20260906, pending).
req(r014, e011, 30000, software, dyne, 20260712, pending).
req(r015, e011, 20000, hardware, bolt, 20260730, pending).
req(r016, e014, 90000, capital, cog, 20260829, pending).
req(r017, e003, 45000, software, bolt, 20260610, pending).
req(r018, e007, 30000, software, edge, 20260820, pending).
emergency(r008).
emergency(r010).
emergency(r017).
violation(e009).
booked(cc1_1, 122000).
booked(cc1_2, 120000).
booked(cc2_1, 98000).
booked(cc2_2, 110000).
cap(company, 630000).
cap(cc1, 254000).
cap(cc1_1, 134000).
cap(cc1_2, 132000).
cap(cc2, 312000).
cap(cc2_1, 95000).
cap(cc2_2, 132000).
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
assignment(e008, cc1_1, hr, 20260101).
assignment(e009, cc1_2, finance, 20260101).
assignment(e009, cc1_2, hr, 20260101).
assignment(e010, cc1_2, finance, 20260101).
assignment(e010, cc1_2, hr, 20260101).
assignment(e011, cc2_1, finance, 20260101).
assignment(e011, cc2_1, hr, 20260101).
assignment(e012, cc2_1, finance, 20260101).
assignment(e012, cc2_2, finance, 20260728).
assignment(e012, cc2_1, hr, 20260101).
assignment(e012, cc2_2, hr, 20260721).
assignment(e013, cc2_2, finance, 20260101).
assignment(e013, cc2_2, hr, 20260101).
assignment(e013, cc1_2, hr, 20260829).
assignment(e014, cc2_2, finance, 20260101).
assignment(e014, cc2_2, hr, 20260101).
exemption(capex, capital, 20260101).
exemption_withdrawn(capex, 20260810).
