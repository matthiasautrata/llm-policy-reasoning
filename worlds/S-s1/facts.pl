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
org_unit(cc1_1, delivery).
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
emp(e011, analyst, cc2_2).
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
reports(e008, e002).
reports(e009, e003).
reports(e010, e003).
reports(e011, e006).
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
req(r001, e011, 3000, hardware, cog, 20260723, pending).
req(r002, e008, 90000, capital, fern, 20260622, pending).
req(r003, e008, 8000, software, fern, 20260808, pending).
req(r004, e005, 90000, services, bolt, 20260705, pending).
req(r005, e010, 120000, hardware, dyne, 20260628, cancelled).
req(r006, e011, 38000, services, cog, 20260910, pending).
req(r007, e011, 60000, capital, cog, 20260617, pending).
req(r008, e004, 12000, software, cog, 20260826, pending).
req(r009, e009, 60000, capital, cog, 20260801, pending).
req(r010, e007, 120000, services, edge, 20260615, cancelled).
req(r011, e008, 8000, software, acme, 20260912, pending).
req(r012, e008, 20000, software, fern, 20260704, pending).
req(r013, e014, 38000, services, edge, 20260814, pending).
req(r014, e008, 20000, hardware, bolt, 20260623, pending).
req(r015, e011, 12000, hardware, fern, 20260614, pending).
req(r016, e002, 90000, hardware, bolt, 20260702, pending).
req(r017, e001, 3000, software, acme, 20260827, cancelled).
req(r018, e013, 38000, services, acme, 20260619, pending).
emergency(r002).
emergency(r004).
emergency(r015).
violation(e008).
booked(cc1_1, 47000).
booked(cc1_2, 137000).
booked(cc2_1, 75000).
booked(cc2_2, 101000).
cap(company, 432000).
cap(cc1, 211000).
cap(cc1_1, 56000).
cap(cc1_2, 219000).
cap(cc2, 264000).
cap(cc2_1, 72000).
cap(cc2_2, 104000).
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
assignment(e011, cc2_2, finance, 20260718).
assignment(e011, cc2_1, hr, 20260101).
assignment(e011, cc2_2, hr, 20260619).
assignment(e012, cc2_1, finance, 20260101).
assignment(e012, cc2_1, hr, 20260101).
assignment(e013, cc2_2, finance, 20260101).
assignment(e013, cc2_2, hr, 20260101).
assignment(e013, cc1_1, hr, 20260902).
assignment(e014, cc2_2, finance, 20260101).
assignment(e014, cc2_2, hr, 20260101).
exemption(capex, capital, 20260101).
exemption_withdrawn(capex, 20260810).
