# Procurement records (L1)

Each table below is one kind of record. Dates are YYYY-MM-DD.

## cc

A cost centre.
Identified by: cc.

| cc |
|---|
| company |
| cc1 |
| cc1_1 |
| cc1_1_1 |
| cc1_1_2 |
| cc1_1_3 |
| cc1_2 |
| cc1_2_1 |
| cc1_2_2 |
| cc1_2_3 |
| cc1_3 |
| cc1_3_1 |
| cc1_3_2 |
| cc1_3_3 |
| cc2 |
| cc2_1 |
| cc2_1_1 |
| cc2_1_2 |
| cc2_1_3 |
| cc2_2 |
| cc2_2_1 |
| cc2_2_2 |
| cc2_2_3 |
| cc2_3 |
| cc2_3_1 |
| cc2_3_2 |
| cc2_3_3 |
| cc3 |
| cc3_1 |
| cc3_1_1 |
| cc3_1_2 |
| cc3_1_3 |
| cc3_2 |
| cc3_2_1 |
| cc3_2_2 |
| cc3_2_3 |
| cc3_3 |
| cc3_3_1 |
| cc3_3_2 |
| cc3_3_3 |

## cc_parent

The parent of a cost centre. The root cost centre has no row.
Identified by: cc. References: `cc` refers to `cc`; `parent` refers to `cc`.

| cc | parent |
|---|---|
| cc1 | company |
| cc1_1 | cc1 |
| cc1_1_1 | cc1_1 |
| cc1_1_2 | cc1_1 |
| cc1_1_3 | cc1_1 |
| cc1_2 | cc1 |
| cc1_2_1 | cc1_2 |
| cc1_2_2 | cc1_2 |
| cc1_2_3 | cc1_2 |
| cc1_3 | cc1 |
| cc1_3_1 | cc1_3 |
| cc1_3_2 | cc1_3 |
| cc1_3_3 | cc1_3 |
| cc2 | company |
| cc2_1 | cc2 |
| cc2_1_1 | cc2_1 |
| cc2_1_2 | cc2_1 |
| cc2_1_3 | cc2_1 |
| cc2_2 | cc2 |
| cc2_2_1 | cc2_2 |
| cc2_2_2 | cc2_2 |
| cc2_2_3 | cc2_2 |
| cc2_3 | cc2 |
| cc2_3_1 | cc2_3 |
| cc2_3_2 | cc2_3 |
| cc2_3_3 | cc2_3 |
| cc3 | company |
| cc3_1 | cc3 |
| cc3_1_1 | cc3_1 |
| cc3_1_2 | cc3_1 |
| cc3_1_3 | cc3_1 |
| cc3_2 | cc3 |
| cc3_2_1 | cc3_2 |
| cc3_2_2 | cc3_2 |
| cc3_2_3 | cc3_2 |
| cc3_3 | cc3 |
| cc3_3_1 | cc3_3 |
| cc3_3_2 | cc3_3 |
| cc3_3_3 | cc3_3 |

## org_unit

The organisational unit a cost centre belongs to.
Identified by: cc. References: `cc` refers to `cc`.

| cc | unit |
|---|---|
| company | leadership |
| cc1 | leadership |
| cc1_1 | leadership |
| cc1_1_1 | support |
| cc1_1_2 | delivery |
| cc1_1_3 | delivery |
| cc1_2 | leadership |
| cc1_2_1 | support |
| cc1_2_2 | delivery |
| cc1_2_3 | support |
| cc1_3 | leadership |
| cc1_3_1 | support |
| cc1_3_2 | support |
| cc1_3_3 | delivery |
| cc2 | leadership |
| cc2_1 | leadership |
| cc2_1_1 | support |
| cc2_1_2 | delivery |
| cc2_1_3 | delivery |
| cc2_2 | leadership |
| cc2_2_1 | support |
| cc2_2_2 | delivery |
| cc2_2_3 | support |
| cc2_3 | leadership |
| cc2_3_1 | support |
| cc2_3_2 | delivery |
| cc2_3_3 | delivery |
| cc3 | leadership |
| cc3_1 | leadership |
| cc3_1_1 | delivery |
| cc3_1_2 | support |
| cc3_1_3 | support |
| cc3_2 | leadership |
| cc3_2_1 | support |
| cc3_2_2 | support |
| cc3_2_3 | delivery |
| cc3_3 | leadership |
| cc3_3_1 | delivery |
| cc3_3_2 | delivery |
| cc3_3_3 | support |

## emp

An employee, their role, and their cost centre in the finance system of record.
Identified by: emp. References: `cc` refers to `cc`.

| emp | role | cc |
|---|---|---|
| e000 | vp | company |
| e001 | director | cc1 |
| e002 | senior_manager | cc1_1 |
| e003 | manager | cc1_1_1 |
| e004 | manager | cc1_1_2 |
| e005 | manager | cc1_1_3 |
| e006 | senior_manager | cc1_2 |
| e007 | manager | cc1_2_1 |
| e008 | manager | cc1_2_2 |
| e009 | manager | cc1_2_3 |
| e010 | senior_manager | cc1_3 |
| e011 | manager | cc1_3_1 |
| e012 | manager | cc1_3_2 |
| e013 | manager | cc1_3_3 |
| e014 | director | cc2 |
| e015 | senior_manager | cc2_1 |
| e016 | manager | cc2_1_1 |
| e017 | manager | cc2_1_2 |
| e018 | manager | cc2_1_3 |
| e019 | senior_manager | cc2_2 |
| e020 | manager | cc2_2_1 |
| e021 | manager | cc2_2_2 |
| e022 | manager | cc2_2_3 |
| e023 | senior_manager | cc2_3 |
| e024 | manager | cc2_3_1 |
| e025 | manager | cc2_3_2 |
| e026 | manager | cc2_3_3 |
| e027 | director | cc3 |
| e028 | senior_manager | cc3_1 |
| e029 | manager | cc3_1_1 |
| e030 | manager | cc3_1_2 |
| e031 | manager | cc3_1_3 |
| e032 | senior_manager | cc3_2 |
| e033 | manager | cc3_2_1 |
| e034 | manager | cc3_2_2 |
| e035 | manager | cc3_2_3 |
| e036 | senior_manager | cc3_3 |
| e037 | manager | cc3_3_1 |
| e038 | manager | cc3_3_2 |
| e039 | manager | cc3_3_3 |
| e040 | analyst | cc1_1_1 |
| e041 | analyst | cc1_1_1 |
| e042 | analyst | cc1_1_1 |
| e043 | analyst | cc1_1_2 |
| e044 | analyst | cc2_1_1 |
| e045 | analyst | cc1_1_2 |
| e046 | analyst | cc1_1_3 |
| e047 | analyst | cc1_1_3 |
| e048 | analyst | cc1_1_3 |
| e049 | analyst | cc1_2_1 |
| e050 | analyst | cc1_2_1 |
| e051 | analyst | cc1_2_1 |
| e052 | analyst | cc1_2_2 |
| e053 | analyst | cc1_2_2 |
| e054 | analyst | cc2_2_2 |
| e055 | analyst | cc1_2_3 |
| e056 | analyst | cc1_2_3 |
| e057 | analyst | cc1_2_3 |
| e058 | analyst | cc1_3_1 |
| e059 | analyst | cc1_3_1 |
| e060 | analyst | cc1_3_1 |
| e061 | analyst | cc1_3_2 |
| e062 | analyst | cc1_3_2 |
| e063 | analyst | cc1_2_3 |
| e064 | analyst | cc1_3_3 |
| e065 | analyst | cc1_3_3 |
| e066 | analyst | cc1_3_3 |
| e067 | analyst | cc2_1_1 |
| e068 | analyst | cc2_1_1 |
| e069 | analyst | cc2_1_1 |
| e070 | analyst | cc2_1_2 |
| e071 | analyst | cc2_1_2 |
| e072 | analyst | cc2_1_2 |
| e073 | analyst | cc2_1_3 |
| e074 | analyst | cc2_1_3 |
| e075 | analyst | cc2_1_3 |
| e076 | analyst | cc2_2_1 |
| e077 | analyst | cc2_2_1 |
| e078 | analyst | cc2_2_1 |
| e079 | analyst | cc2_2_2 |
| e080 | analyst | cc2_2_2 |
| e081 | analyst | cc2_2_2 |
| e082 | analyst | cc2_2_3 |
| e083 | analyst | cc2_2_3 |
| e084 | analyst | cc2_2_3 |
| e085 | analyst | cc2_3_1 |
| e086 | analyst | cc2_3_1 |
| e087 | analyst | cc2_1_1 |
| e088 | analyst | cc2_3_2 |
| e089 | analyst | cc2_3_2 |
| e090 | analyst | cc2_3_2 |
| e091 | analyst | cc2_3_3 |
| e092 | analyst | cc2_3_3 |
| e093 | analyst | cc2_3_3 |
| e094 | analyst | cc3_1_1 |
| e095 | analyst | cc3_1_1 |
| e096 | analyst | cc3_1_1 |
| e097 | analyst | cc3_1_2 |
| e098 | analyst | cc3_1_2 |
| e099 | analyst | cc3_1_2 |
| e100 | analyst | cc3_1_3 |
| e101 | analyst | cc3_1_3 |
| e102 | analyst | cc3_1_3 |
| e103 | analyst | cc3_2_1 |
| e104 | analyst | cc3_2_1 |
| e105 | analyst | cc3_2_1 |
| e106 | analyst | cc3_2_2 |
| e107 | analyst | cc3_2_2 |
| e108 | analyst | cc3_2_2 |
| e109 | analyst | cc3_2_3 |
| e110 | analyst | cc3_2_3 |
| e111 | analyst | cc3_1_2 |
| e112 | analyst | cc3_3_1 |
| e113 | analyst | cc3_3_1 |
| e114 | analyst | cc3_3_1 |
| e115 | analyst | cc3_3_2 |
| e116 | analyst | cc3_3_2 |
| e117 | analyst | cc3_3_2 |
| e118 | analyst | cc3_3_3 |
| e119 | analyst | cc3_3_3 |
| e120 | analyst | cc3_3_3 |

## reports

An employee's direct manager.
Identified by: emp. References: `emp` refers to `emp`; `manager` refers to `emp`.

| emp | manager |
|---|---|
| e001 | e000 |
| e002 | e001 |
| e003 | e002 |
| e004 | e002 |
| e005 | e002 |
| e006 | e001 |
| e007 | e006 |
| e008 | e006 |
| e009 | e006 |
| e010 | e001 |
| e011 | e010 |
| e012 | e010 |
| e013 | e010 |
| e014 | e000 |
| e015 | e014 |
| e016 | e015 |
| e017 | e015 |
| e018 | e015 |
| e019 | e014 |
| e020 | e019 |
| e021 | e019 |
| e022 | e019 |
| e023 | e014 |
| e024 | e023 |
| e025 | e023 |
| e026 | e023 |
| e027 | e000 |
| e028 | e027 |
| e029 | e028 |
| e030 | e028 |
| e031 | e028 |
| e032 | e027 |
| e033 | e032 |
| e034 | e032 |
| e035 | e032 |
| e036 | e027 |
| e037 | e036 |
| e038 | e036 |
| e039 | e036 |
| e040 | e003 |
| e041 | e003 |
| e042 | e003 |
| e043 | e004 |
| e044 | e016 |
| e045 | e004 |
| e046 | e005 |
| e047 | e005 |
| e048 | e005 |
| e049 | e007 |
| e050 | e007 |
| e051 | e007 |
| e052 | e008 |
| e053 | e008 |
| e054 | e021 |
| e055 | e009 |
| e056 | e009 |
| e057 | e009 |
| e058 | e011 |
| e059 | e011 |
| e060 | e011 |
| e061 | e012 |
| e062 | e012 |
| e063 | e009 |
| e064 | e013 |
| e065 | e013 |
| e066 | e013 |
| e067 | e016 |
| e068 | e016 |
| e069 | e016 |
| e070 | e017 |
| e071 | e017 |
| e072 | e017 |
| e073 | e018 |
| e074 | e018 |
| e075 | e018 |
| e076 | e020 |
| e077 | e020 |
| e078 | e020 |
| e079 | e021 |
| e080 | e021 |
| e081 | e021 |
| e082 | e022 |
| e083 | e022 |
| e084 | e022 |
| e085 | e024 |
| e086 | e024 |
| e087 | e016 |
| e088 | e025 |
| e089 | e025 |
| e090 | e025 |
| e091 | e026 |
| e092 | e026 |
| e093 | e026 |
| e094 | e029 |
| e095 | e029 |
| e096 | e029 |
| e097 | e030 |
| e098 | e030 |
| e099 | e030 |
| e100 | e031 |
| e101 | e031 |
| e102 | e031 |
| e103 | e033 |
| e104 | e033 |
| e105 | e033 |
| e106 | e034 |
| e107 | e034 |
| e108 | e034 |
| e109 | e035 |
| e110 | e035 |
| e111 | e030 |
| e112 | e037 |
| e113 | e037 |
| e114 | e037 |
| e115 | e038 |
| e116 | e038 |
| e117 | e038 |
| e118 | e039 |
| e119 | e039 |
| e120 | e039 |

## role_limit

The approval limit currently attached to a role.
Identified by: role.

| role | limit |
|---|---|
| analyst | 5000 |
| manager | 40000 |
| senior_manager | 50000 |
| director | 100000 |
| vp | 500000 |

## vendor

A vendor and its current status (approved or suspended).
Identified by: vendor.

| vendor | status |
|---|---|
| acme | approved |
| bolt | suspended |
| cog | approved |
| dyne | approved |
| edge | approved |
| fern | suspended |

## req

A purchase request, raised on the given date; status is pending or cancelled.
Identified by: req. References: `requester` refers to `emp`; `vendor` refers to `vendor`.

| req | requester | amount | category | vendor | date | status |
|---|---|---|---|---|---|---|
| r001 | e040 | 38000 | services | acme | 2026-07-16 | pending |
| r002 | e115 | 38000 | services | acme | 2026-07-14 | pending |
| r003 | e114 | 30000 | software | edge | 2026-07-05 | pending |
| r004 | e050 | 60000 | hardware | acme | 2026-09-04 | cancelled |
| r005 | e055 | 90000 | hardware | edge | 2026-06-23 | pending |
| r006 | e046 | 120000 | services | dyne | 2026-06-12 | pending |
| r007 | e040 | 120000 | software | cog | 2026-08-25 | pending |
| r008 | e006 | 45000 | hardware | dyne | 2026-06-22 | pending |
| r009 | e083 | 38000 | hardware | acme | 2026-08-15 | pending |
| r010 | e064 | 3000 | hardware | acme | 2026-08-16 | pending |
| r011 | e029 | 90000 | hardware | fern | 2026-07-18 | pending |
| r012 | e063 | 45000 | hardware | bolt | 2026-09-03 | pending |
| r013 | e032 | 120000 | software | fern | 2026-09-07 | pending |
| r014 | e046 | 38000 | software | dyne | 2026-07-06 | pending |
| r015 | e052 | 20000 | services | edge | 2026-07-17 | pending |
| r016 | e072 | 120000 | services | acme | 2026-07-09 | pending |
| r017 | e038 | 38000 | software | dyne | 2026-08-24 | pending |
| r018 | e077 | 38000 | hardware | bolt | 2026-07-08 | pending |
| r019 | e070 | 20000 | hardware | bolt | 2026-07-30 | pending |
| r020 | e039 | 12000 | capital | fern | 2026-09-14 | pending |
| r021 | e100 | 8000 | capital | fern | 2026-07-24 | pending |
| r022 | e077 | 120000 | hardware | fern | 2026-08-08 | pending |
| r023 | e042 | 3000 | hardware | edge | 2026-08-07 | pending |
| r024 | e021 | 8000 | hardware | bolt | 2026-07-08 | pending |
| r025 | e105 | 8000 | hardware | edge | 2026-07-25 | cancelled |
| r026 | e064 | 120000 | capital | fern | 2026-06-04 | pending |
| r027 | e041 | 45000 | software | dyne | 2026-09-07 | pending |
| r028 | e093 | 3000 | capital | dyne | 2026-08-06 | pending |
| r029 | e011 | 60000 | services | dyne | 2026-09-05 | cancelled |
| r030 | e051 | 45000 | hardware | edge | 2026-06-30 | pending |
| r031 | e045 | 20000 | software | dyne | 2026-08-22 | cancelled |
| r032 | e065 | 90000 | services | dyne | 2026-06-05 | pending |
| r033 | e018 | 45000 | services | acme | 2026-08-14 | pending |
| r034 | e088 | 12000 | services | dyne | 2026-06-22 | cancelled |
| r035 | e093 | 12000 | software | cog | 2026-07-12 | pending |
| r036 | e045 | 30000 | software | fern | 2026-07-31 | pending |
| r037 | e079 | 120000 | capital | fern | 2026-06-29 | pending |
| r038 | e022 | 12000 | capital | bolt | 2026-08-19 | pending |
| r039 | e060 | 12000 | software | cog | 2026-07-03 | pending |
| r040 | e047 | 12000 | software | edge | 2026-09-05 | pending |
| r041 | e086 | 8000 | services | cog | 2026-06-06 | pending |
| r042 | e069 | 12000 | hardware | cog | 2026-08-18 | pending |
| r043 | e001 | 12000 | capital | bolt | 2026-09-10 | pending |
| r044 | e048 | 20000 | capital | bolt | 2026-09-06 | pending |
| r045 | e019 | 3000 | services | dyne | 2026-09-06 | pending |
| r046 | e066 | 20000 | hardware | fern | 2026-08-15 | pending |
| r047 | e052 | 30000 | capital | bolt | 2026-07-15 | pending |
| r048 | e021 | 12000 | hardware | bolt | 2026-09-14 | pending |
| r049 | e119 | 90000 | capital | fern | 2026-09-12 | pending |
| r050 | e045 | 90000 | hardware | edge | 2026-08-29 | pending |
| r051 | e013 | 45000 | hardware | acme | 2026-07-04 | pending |
| r052 | e097 | 12000 | software | bolt | 2026-09-04 | pending |
| r053 | e025 | 30000 | hardware | acme | 2026-07-08 | cancelled |
| r054 | e119 | 12000 | software | bolt | 2026-08-31 | cancelled |
| r055 | e071 | 45000 | services | cog | 2026-08-15 | pending |
| r056 | e104 | 45000 | capital | dyne | 2026-06-27 | pending |
| r057 | e117 | 120000 | services | dyne | 2026-06-10 | pending |
| r058 | e013 | 60000 | software | cog | 2026-06-25 | pending |
| r059 | e051 | 120000 | hardware | bolt | 2026-08-27 | pending |
| r060 | e027 | 90000 | hardware | fern | 2026-06-27 | pending |
| r061 | e097 | 20000 | services | cog | 2026-06-03 | pending |
| r062 | e115 | 8000 | software | acme | 2026-06-04 | pending |
| r063 | e044 | 3000 | software | fern | 2026-06-24 | pending |
| r064 | e055 | 90000 | capital | fern | 2026-09-13 | cancelled |
| r065 | e070 | 60000 | services | cog | 2026-08-29 | pending |
| r066 | e048 | 90000 | hardware | edge | 2026-08-08 | pending |
| r067 | e110 | 90000 | capital | cog | 2026-08-27 | pending |
| r068 | e120 | 90000 | capital | dyne | 2026-07-15 | pending |
| r069 | e117 | 20000 | hardware | edge | 2026-07-16 | pending |
| r070 | e020 | 20000 | software | bolt | 2026-08-17 | pending |
| r071 | e065 | 12000 | services | acme | 2026-07-16 | pending |
| r072 | e107 | 12000 | software | cog | 2026-08-13 | pending |
| r073 | e106 | 30000 | services | edge | 2026-07-30 | pending |
| r074 | e106 | 30000 | hardware | edge | 2026-08-07 | cancelled |
| r075 | e119 | 30000 | services | bolt | 2026-08-01 | pending |
| r076 | e099 | 120000 | services | fern | 2026-09-05 | pending |
| r077 | e105 | 60000 | software | dyne | 2026-06-02 | pending |
| r078 | e045 | 12000 | services | cog | 2026-06-11 | pending |
| r079 | e011 | 20000 | hardware | acme | 2026-06-07 | pending |
| r080 | e053 | 60000 | capital | cog | 2026-06-18 | pending |
| r081 | e012 | 120000 | services | fern | 2026-08-22 | pending |
| r082 | e013 | 30000 | hardware | bolt | 2026-07-06 | pending |
| r083 | e095 | 20000 | services | bolt | 2026-07-16 | pending |
| r084 | e031 | 8000 | software | fern | 2026-07-15 | pending |
| r085 | e061 | 90000 | services | dyne | 2026-07-19 | pending |
| r086 | e116 | 38000 | software | dyne | 2026-07-26 | pending |
| r087 | e056 | 60000 | hardware | dyne | 2026-06-13 | pending |
| r088 | e030 | 30000 | hardware | cog | 2026-09-13 | pending |
| r089 | e019 | 60000 | capital | acme | 2026-06-29 | pending |
| r090 | e096 | 3000 | software | cog | 2026-09-15 | pending |
| r091 | e087 | 20000 | services | acme | 2026-07-07 | pending |
| r092 | e033 | 38000 | services | dyne | 2026-07-09 | pending |
| r093 | e114 | 60000 | software | edge | 2026-07-25 | pending |
| r094 | e077 | 60000 | software | bolt | 2026-08-10 | pending |
| r095 | e089 | 30000 | software | fern | 2026-06-05 | pending |
| r096 | e078 | 90000 | hardware | dyne | 2026-08-18 | pending |
| r097 | e093 | 20000 | services | acme | 2026-09-11 | pending |
| r098 | e082 | 20000 | services | fern | 2026-07-11 | pending |
| r099 | e026 | 3000 | hardware | fern | 2026-08-16 | pending |
| r100 | e050 | 12000 | hardware | cog | 2026-08-18 | pending |
| r101 | e084 | 12000 | hardware | fern | 2026-09-01 | pending |
| r102 | e057 | 20000 | capital | cog | 2026-09-04 | pending |

## emergency

A request flagged as an emergency.
Identified by: req. References: `req` refers to `req`.

| req |
|---|
| r006 |
| r010 |
| r011 |
| r016 |
| r020 |
| r026 |
| r030 |
| r036 |
| r037 |
| r044 |
| r048 |
| r049 |
| r060 |
| r061 |
| r063 |
| r066 |
| r067 |
| r068 |
| r075 |
| r084 |
| r085 |
| r087 |
| r093 |
| r097 |
| r098 |
| r101 |

## violation

An employee with a recorded policy violation.
Identified by: emp. References: `emp` refers to `emp`.

| emp |
|---|
| e013 |
| e014 |
| e047 |
| e063 |
| e076 |
| e081 |
| e088 |
| e101 |
| e107 |
| e113 |
| e115 |
| e118 |

## booked

Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| cc1_1_1 | 100000 |
| cc1_1_2 | 139000 |
| cc1_1_3 | 47000 |
| cc1_2_1 | 105000 |
| cc1_2_2 | 45000 |
| cc1_2_3 | 119000 |
| cc1_3_1 | 125000 |
| cc1_3_2 | 44000 |
| cc1_3_3 | 98000 |
| cc2_1_1 | 120000 |
| cc2_1_2 | 125000 |
| cc2_1_3 | 46000 |
| cc2_2_1 | 54000 |
| cc2_2_2 | 68000 |
| cc2_2_3 | 111000 |
| cc2_3_1 | 124000 |
| cc2_3_2 | 76000 |
| cc2_3_3 | 99000 |
| cc3_1_1 | 67000 |
| cc3_1_2 | 71000 |
| cc3_1_3 | 87000 |
| cc3_2_1 | 42000 |
| cc3_2_2 | 106000 |
| cc3_2_3 | 63000 |
| cc3_3_1 | 91000 |
| cc3_3_2 | 95000 |
| cc3_3_3 | 119000 |
| cc2_3 | 38000 |
| cc3_2 | 22000 |

## cap

The spending cap of a cost centre this quarter.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| company | 2935000 |
| cc1 | 863000 |
| cc1_1 | 429000 |
| cc1_1_1 | 97000 |
| cc1_1_2 | 166000 |
| cc1_1_3 | 45000 |
| cc1_2 | 309000 |
| cc1_2_1 | 147000 |
| cc1_2_2 | 62000 |
| cc1_2_3 | 166000 |
| cc1_3 | 307000 |
| cc1_3_1 | 128000 |
| cc1_3_2 | 70000 |
| cc1_3_3 | 100000 |
| cc2 | 1291000 |
| cc2_1 | 436000 |
| cc2_1_1 | 168000 |
| cc2_1_2 | 128000 |
| cc2_1_3 | 64000 |
| cc2_2 | 302000 |
| cc2_2_1 | 52000 |
| cc2_2_2 | 65000 |
| cc2_2_3 | 177000 |
| cc2_3 | 505000 |
| cc2_3_1 | 198000 |
| cc2_3_2 | 78000 |
| cc2_3_3 | 101000 |
| cc3 | 1144000 |
| cc3_1 | 292000 |
| cc3_1_1 | 69000 |
| cc3_1_2 | 113000 |
| cc3_1_3 | 84000 |
| cc3_2 | 302000 |
| cc3_2_1 | 43000 |
| cc3_2_2 | 109000 |
| cc3_2_3 | 88000 |
| cc3_3 | 396000 |
| cc3_3_1 | 127000 |
| cc3_3_2 | 114000 |
| cc3_3_3 | 122000 |

# Terms

What the terms used below refer to in the records.

- **requester** (`req.requester`): The requester of a request is the employee who raised it.
- **requester's cost centre** (`emp.cc`): A requester's cost centre is the cost centre recorded for them in emp.
- **pending request** (`req.status = pending`): A pending request is one whose status is pending. Cancelled requests are neither pending nor booked.
- **booked amount** (`booked.amount`): The booked amount of a cost centre is what is booked directly on it. Its booked total is defined separately (R104).
- **cap** (`cap.amount`): The cap of a cost centre bounds its committed spend (R106).
- **manager** (`reports.manager`): An employee's manager is their direct manager only. Their reporting chain (R103) goes further up.
- **organisational unit** (`org_unit.unit`): The organisational unit of a cost centre is a grouping of cost centres. An employee's department is defined separately (R113).

# Definitions

Each definition has a rule id. A definition applies wherever its term is used.

- **R101.** The ancestors of a cost centre are its parent, its parent's parent, and so on.
- **R102.** A cost centre lies in the subtree of a cost centre X if it is X or one of X's descendants.
- **R103.** An employee's reporting chain is their manager, their manager's manager, and so on. It does not include the employee.
- **R104.** The booked total of a cost centre is the sum of the booked amounts of every cost centre in its subtree (zero where nothing is booked).
- **R105.** The pending total of a cost centre is the sum of the amounts of pending requests whose requester's cost centre lies in its subtree.
- **R106.** The committed spend of a cost centre is its booked total. Pending requests do not count.
- **R107.** The headroom of a cost centre is its cap minus its committed spend.
- **R108.** A cost centre is over cap if its committed spend exceeds its cap.
- **R109.** A request's cap scope is its requester's cost centre and every ancestor of that cost centre.
- **R110.** A request's exposure at a cost centre in its cap scope is that centre's committed spend plus the request amount, not counting the request itself twice if committed spend already includes it.
- **R111.** A request breaches a cap if its exposure at some cost centre in its cap scope exceeds that centre's cap.
- **R112.** A big capital request is a capital request whose amount is over 50000.
- **R113.** An employee's department is their cost centre.
- **R114.** The headcount of a department is the number of employees whose department it is.

# Decisions

Questions of interpretation, who decides them, and what was decided. The definitions above already follow these decisions.

- **c1** (owner: controller), on committed spend: Does the committed spend of a cost centre include pending requests? Decided: booked_only.
- **c3** (owner: hr), on department: Is an employee's department their cost centre or their cost centre's organisational unit? Decided: cost_centre.
- **c4** (owner: controller), on cap scope: Does a request's cap check cover only the requester's cost centre, or also every ancestor of it? Decided: with_ancestors.
- **c6** (owner: controller), on booked total: Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it? Decided: with_descendants.
