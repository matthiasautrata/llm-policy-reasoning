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
| cc1_1_1 | delivery |
| cc1_1_2 | support |
| cc1_1_3 | support |
| cc1_2 | leadership |
| cc1_2_1 | delivery |
| cc1_2_2 | delivery |
| cc1_2_3 | delivery |
| cc1_3 | leadership |
| cc1_3_1 | delivery |
| cc1_3_2 | support |
| cc1_3_3 | support |
| cc2 | leadership |
| cc2_1 | leadership |
| cc2_1_1 | delivery |
| cc2_1_2 | delivery |
| cc2_1_3 | delivery |
| cc2_2 | leadership |
| cc2_2_1 | delivery |
| cc2_2_2 | support |
| cc2_2_3 | delivery |
| cc2_3 | leadership |
| cc2_3_1 | delivery |
| cc2_3_2 | support |
| cc2_3_3 | support |
| cc3 | leadership |
| cc3_1 | leadership |
| cc3_1_1 | delivery |
| cc3_1_2 | support |
| cc3_1_3 | support |
| cc3_2 | leadership |
| cc3_2_1 | delivery |
| cc3_2_2 | support |
| cc3_2_3 | support |
| cc3_3 | leadership |
| cc3_3_1 | support |
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
| e043 | analyst | cc1_2_1 |
| e044 | analyst | cc1_1_2 |
| e045 | analyst | cc1_1_2 |
| e046 | analyst | cc1_1_3 |
| e047 | analyst | cc1_1_3 |
| e048 | analyst | cc1_1_3 |
| e049 | analyst | cc1_2_1 |
| e050 | analyst | cc1_2_1 |
| e051 | analyst | cc1_2_1 |
| e052 | analyst | cc1_2_2 |
| e053 | analyst | cc1_2_2 |
| e054 | analyst | cc1_2_2 |
| e055 | analyst | cc1_2_3 |
| e056 | analyst | cc1_2_3 |
| e057 | analyst | cc1_2_3 |
| e058 | analyst | cc1_3_1 |
| e059 | analyst | cc1_3_1 |
| e060 | analyst | cc1_3_1 |
| e061 | analyst | cc1_3_2 |
| e062 | analyst | cc1_3_2 |
| e063 | analyst | cc1_3_2 |
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
| e074 | analyst | cc3_1_1 |
| e075 | analyst | cc2_1_3 |
| e076 | analyst | cc2_2_1 |
| e077 | analyst | cc3_1_3 |
| e078 | analyst | cc2_2_1 |
| e079 | analyst | cc2_2_2 |
| e080 | analyst | cc2_2_2 |
| e081 | analyst | cc2_2_2 |
| e082 | analyst | cc2_2_3 |
| e083 | analyst | cc2_2_3 |
| e084 | analyst | cc2_2_3 |
| e085 | analyst | cc2_3_1 |
| e086 | analyst | cc2_3_1 |
| e087 | analyst | cc2_3_1 |
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
| e099 | analyst | cc2_1_3 |
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
| e110 | analyst | cc3_1_1 |
| e111 | analyst | cc3_2_3 |
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
| e043 | e007 |
| e044 | e004 |
| e045 | e004 |
| e046 | e005 |
| e047 | e005 |
| e048 | e005 |
| e049 | e007 |
| e050 | e007 |
| e051 | e007 |
| e052 | e008 |
| e053 | e008 |
| e054 | e008 |
| e055 | e009 |
| e056 | e009 |
| e057 | e009 |
| e058 | e011 |
| e059 | e011 |
| e060 | e011 |
| e061 | e012 |
| e062 | e012 |
| e063 | e012 |
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
| e074 | e029 |
| e075 | e018 |
| e076 | e020 |
| e077 | e031 |
| e078 | e020 |
| e079 | e021 |
| e080 | e021 |
| e081 | e021 |
| e082 | e022 |
| e083 | e022 |
| e084 | e022 |
| e085 | e024 |
| e086 | e024 |
| e087 | e024 |
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
| e099 | e018 |
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
| e110 | e029 |
| e111 | e035 |
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
| r001 | e065 | 90000 | hardware | dyne | 2026-09-15 | cancelled |
| r002 | e067 | 38000 | services | acme | 2026-07-22 | pending |
| r003 | e095 | 30000 | capital | cog | 2026-08-09 | pending |
| r004 | e004 | 120000 | software | edge | 2026-06-27 | pending |
| r005 | e115 | 8000 | capital | fern | 2026-06-03 | pending |
| r006 | e043 | 3000 | services | edge | 2026-06-15 | pending |
| r007 | e043 | 20000 | software | bolt | 2026-07-29 | pending |
| r008 | e051 | 30000 | services | edge | 2026-09-15 | cancelled |
| r009 | e110 | 60000 | services | dyne | 2026-07-25 | pending |
| r010 | e094 | 45000 | hardware | bolt | 2026-07-23 | pending |
| r011 | e081 | 90000 | capital | fern | 2026-06-26 | pending |
| r012 | e032 | 38000 | capital | edge | 2026-07-15 | pending |
| r013 | e077 | 3000 | hardware | cog | 2026-06-18 | cancelled |
| r014 | e112 | 38000 | services | fern | 2026-08-18 | pending |
| r015 | e106 | 12000 | capital | fern | 2026-08-27 | pending |
| r016 | e081 | 60000 | capital | cog | 2026-06-06 | pending |
| r017 | e018 | 3000 | capital | dyne | 2026-08-11 | pending |
| r018 | e056 | 12000 | software | acme | 2026-09-11 | pending |
| r019 | e092 | 8000 | hardware | dyne | 2026-06-10 | pending |
| r020 | e069 | 8000 | services | cog | 2026-08-22 | pending |
| r021 | e012 | 20000 | services | fern | 2026-06-15 | cancelled |
| r022 | e021 | 12000 | hardware | dyne | 2026-06-09 | pending |
| r023 | e061 | 20000 | software | bolt | 2026-08-24 | pending |
| r024 | e107 | 8000 | software | acme | 2026-08-24 | pending |
| r025 | e094 | 8000 | services | fern | 2026-09-06 | pending |
| r026 | e046 | 45000 | software | bolt | 2026-09-04 | pending |
| r027 | e087 | 60000 | services | acme | 2026-07-16 | pending |
| r028 | e025 | 3000 | hardware | fern | 2026-08-03 | pending |
| r029 | e098 | 20000 | capital | dyne | 2026-07-11 | pending |
| r030 | e088 | 20000 | software | bolt | 2026-07-30 | pending |
| r031 | e018 | 30000 | software | fern | 2026-09-06 | pending |
| r032 | e067 | 8000 | capital | fern | 2026-08-21 | pending |
| r033 | e044 | 8000 | services | cog | 2026-08-11 | pending |
| r034 | e085 | 120000 | capital | acme | 2026-09-12 | pending |
| r035 | e088 | 20000 | capital | dyne | 2026-08-30 | pending |
| r036 | e072 | 30000 | services | edge | 2026-09-03 | pending |
| r037 | e058 | 120000 | services | acme | 2026-08-27 | pending |
| r038 | e086 | 45000 | hardware | dyne | 2026-06-24 | pending |
| r039 | e076 | 12000 | software | cog | 2026-06-22 | pending |
| r040 | e078 | 45000 | services | acme | 2026-06-17 | pending |
| r041 | e045 | 45000 | capital | dyne | 2026-09-06 | pending |
| r042 | e025 | 8000 | software | edge | 2026-08-29 | pending |
| r043 | e045 | 120000 | hardware | fern | 2026-08-12 | pending |
| r044 | e102 | 90000 | services | acme | 2026-08-26 | pending |
| r045 | e020 | 90000 | services | dyne | 2026-07-11 | pending |
| r046 | e007 | 12000 | software | fern | 2026-08-10 | pending |
| r047 | e033 | 12000 | services | fern | 2026-06-20 | pending |
| r048 | e018 | 30000 | services | acme | 2026-09-01 | pending |
| r049 | e012 | 90000 | software | dyne | 2026-09-07 | pending |
| r050 | e075 | 38000 | services | dyne | 2026-07-18 | pending |
| r051 | e072 | 12000 | software | acme | 2026-07-09 | pending |
| r052 | e089 | 3000 | software | acme | 2026-06-26 | cancelled |
| r053 | e105 | 90000 | software | edge | 2026-06-16 | pending |
| r054 | e048 | 38000 | software | acme | 2026-07-18 | cancelled |
| r055 | e095 | 90000 | software | bolt | 2026-07-29 | cancelled |
| r056 | e085 | 38000 | capital | fern | 2026-06-09 | pending |
| r057 | e104 | 8000 | capital | fern | 2026-07-10 | pending |
| r058 | e026 | 3000 | software | cog | 2026-09-11 | cancelled |
| r059 | e080 | 12000 | hardware | fern | 2026-07-28 | pending |
| r060 | e095 | 120000 | services | cog | 2026-08-10 | pending |
| r061 | e106 | 120000 | capital | fern | 2026-08-28 | pending |
| r062 | e075 | 8000 | services | edge | 2026-09-08 | pending |
| r063 | e032 | 30000 | services | bolt | 2026-06-10 | pending |
| r064 | e093 | 12000 | services | cog | 2026-08-08 | pending |
| r065 | e074 | 38000 | capital | cog | 2026-08-23 | pending |
| r066 | e082 | 20000 | hardware | bolt | 2026-06-02 | pending |
| r067 | e017 | 12000 | capital | cog | 2026-08-25 | pending |
| r068 | e024 | 60000 | software | dyne | 2026-07-21 | pending |
| r069 | e066 | 45000 | capital | acme | 2026-06-20 | cancelled |
| r070 | e028 | 12000 | hardware | cog | 2026-08-26 | pending |
| r071 | e057 | 38000 | services | acme | 2026-06-24 | pending |
| r072 | e040 | 30000 | hardware | fern | 2026-07-15 | pending |
| r073 | e077 | 20000 | services | edge | 2026-08-05 | pending |
| r074 | e109 | 30000 | capital | cog | 2026-08-23 | pending |
| r075 | e053 | 60000 | software | acme | 2026-07-01 | pending |
| r076 | e014 | 38000 | hardware | fern | 2026-06-16 | pending |
| r077 | e092 | 120000 | hardware | fern | 2026-08-18 | pending |
| r078 | e020 | 12000 | software | acme | 2026-06-02 | pending |
| r079 | e104 | 30000 | hardware | fern | 2026-07-08 | pending |
| r080 | e096 | 30000 | hardware | bolt | 2026-06-11 | pending |
| r081 | e014 | 38000 | capital | edge | 2026-08-28 | pending |
| r082 | e115 | 60000 | capital | edge | 2026-07-07 | pending |
| r083 | e099 | 12000 | capital | bolt | 2026-09-15 | cancelled |
| r084 | e032 | 90000 | hardware | bolt | 2026-06-21 | pending |
| r085 | e106 | 20000 | hardware | fern | 2026-07-03 | pending |
| r086 | e038 | 45000 | hardware | edge | 2026-06-19 | pending |
| r087 | e034 | 45000 | services | bolt | 2026-08-26 | pending |
| r088 | e012 | 3000 | capital | cog | 2026-06-08 | pending |
| r089 | e083 | 30000 | software | bolt | 2026-06-21 | pending |
| r090 | e086 | 8000 | software | acme | 2026-07-10 | pending |
| r091 | e083 | 120000 | services | fern | 2026-07-24 | pending |
| r092 | e060 | 120000 | hardware | bolt | 2026-08-01 | pending |
| r093 | e072 | 30000 | services | edge | 2026-06-03 | pending |
| r094 | e068 | 8000 | services | fern | 2026-08-19 | cancelled |
| r095 | e004 | 12000 | services | fern | 2026-06-09 | pending |
| r096 | e063 | 30000 | services | bolt | 2026-06-01 | pending |
| r097 | e117 | 30000 | services | dyne | 2026-08-06 | pending |
| r098 | e088 | 60000 | services | fern | 2026-06-30 | pending |
| r099 | e065 | 45000 | hardware | cog | 2026-06-25 | pending |
| r100 | e030 | 90000 | hardware | acme | 2026-08-14 | pending |
| r101 | e082 | 20000 | capital | dyne | 2026-08-14 | pending |
| r102 | e007 | 45000 | services | bolt | 2026-08-16 | pending |

## emergency

A request flagged as an emergency.
Identified by: req. References: `req` refers to `req`.

| req |
|---|
| r006 |
| r007 |
| r011 |
| r018 |
| r022 |
| r027 |
| r031 |
| r042 |
| r056 |
| r058 |
| r059 |
| r061 |
| r062 |
| r067 |
| r073 |
| r075 |
| r083 |
| r084 |
| r088 |
| r091 |
| r095 |
| r097 |

## violation

An employee with a recorded policy violation.
Identified by: emp. References: `emp` refers to `emp`.

| emp |
|---|
| e006 |
| e026 |
| e028 |
| e034 |
| e043 |
| e054 |
| e062 |
| e069 |
| e070 |
| e086 |
| e097 |
| e107 |

## booked

Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| cc1_1_1 | 63000 |
| cc1_1_2 | 63000 |
| cc1_1_3 | 81000 |
| cc1_2_1 | 115000 |
| cc1_2_2 | 95000 |
| cc1_2_3 | 97000 |
| cc1_3_1 | 126000 |
| cc1_3_2 | 47000 |
| cc1_3_3 | 119000 |
| cc2_1_1 | 47000 |
| cc2_1_2 | 72000 |
| cc2_1_3 | 73000 |
| cc2_2_1 | 62000 |
| cc2_2_2 | 108000 |
| cc2_2_3 | 86000 |
| cc2_3_1 | 73000 |
| cc2_3_2 | 63000 |
| cc2_3_3 | 86000 |
| cc3_1_1 | 113000 |
| cc3_1_2 | 92000 |
| cc3_1_3 | 105000 |
| cc3_2_1 | 69000 |
| cc3_2_2 | 54000 |
| cc3_2_3 | 75000 |
| cc3_3_1 | 56000 |
| cc3_3_2 | 41000 |
| cc3_3_3 | 59000 |
| company | 14000 |
| cc2 | 9000 |
| cc2_2 | 19000 |
| cc3_2 | 29000 |
| cc3_3 | 35000 |

## cap

The spending cap of a cost centre this quarter.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| company | 2695000 |
| cc1 | 926000 |
| cc1_1 | 238000 |
| cc1_1_1 | 100000 |
| cc1_1_2 | 61000 |
| cc1_1_3 | 78000 |
| cc1_2 | 399000 |
| cc1_2_1 | 184000 |
| cc1_2_2 | 133000 |
| cc1_2_3 | 94000 |
| cc1_3 | 306000 |
| cc1_3_1 | 176000 |
| cc1_3_2 | 48000 |
| cc1_3_3 | 115000 |
| cc2 | 732000 |
| cc2_1 | 220000 |
| cc2_1_1 | 75000 |
| cc2_1_2 | 86000 |
| cc2_1_3 | 116000 |
| cc2_2 | 288000 |
| cc2_2_1 | 63000 |
| cc2_2_2 | 151000 |
| cc2_2_3 | 83000 |
| cc2_3 | 255000 |
| cc2_3_1 | 102000 |
| cc2_3_2 | 61000 |
| cc2_3_3 | 103000 |
| cc3 | 946000 |
| cc3_1 | 465000 |
| cc3_1_1 | 158000 |
| cc3_1_2 | 128000 |
| cc3_1_3 | 101000 |
| cc3_2 | 340000 |
| cc3_2_1 | 110000 |
| cc3_2_2 | 55000 |
| cc3_2_3 | 90000 |
| cc3_3 | 219000 |
| cc3_3_1 | 78000 |
| cc3_3_2 | 65000 |
| cc3_3_3 | 82000 |

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
- **Open question c6** (owner: controller), on booked total: Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it? This has not been decided. The readings are:
  - with_descendants (R104): The booked total of a cost centre is the sum of the booked amounts of every cost centre in its subtree (zero where nothing is booked).
  - direct_only (R104b): The booked total of a cost centre is its own booked amount, not counting its descendants (zero where nothing is booked).
- **R105.** The pending total of a cost centre is the sum of the amounts of pending requests whose requester's cost centre lies in its subtree.
- **Open question c1** (owner: controller), on committed spend: Does the committed spend of a cost centre include pending requests? This has not been decided. The readings are:
  - booked_only (R106): The committed spend of a cost centre is its booked total. Pending requests do not count.
  - with_pending (R106b): The committed spend of a cost centre is its booked total plus its pending total.
- **R107.** The headroom of a cost centre is its cap minus its committed spend.
- **R108.** A cost centre is over cap if its committed spend exceeds its cap.
- **Open question c4** (owner: controller), on cap scope: Does a request's cap check cover only the requester's cost centre, or also every ancestor of it? This has not been decided. The readings are:
  - with_ancestors (R109): A request's cap scope is its requester's cost centre and every ancestor of that cost centre.
  - own_only (R109b): A request's cap scope is its requester's cost centre only.
- **R110.** A request's exposure at a cost centre in its cap scope is that centre's committed spend plus the request amount, not counting the request itself twice if committed spend already includes it.
- **R111.** A request breaches a cap if its exposure at some cost centre in its cap scope exceeds that centre's cap.
- **R112.** A big capital request is a capital request whose amount is over 50000.
- **Open question c3** (owner: hr), on department: Is an employee's department their cost centre or their cost centre's organisational unit? This has not been decided. The readings are:
  - cost_centre (R113): An employee's department is their cost centre.
  - org_unit (R113b): An employee's department is the organisational unit of their cost centre.
- **R114.** The headcount of a department is the number of employees whose department it is.
