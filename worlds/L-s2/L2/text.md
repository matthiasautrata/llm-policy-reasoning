# Procurement records (L2)

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
| cc1_1_1_1 |
| cc1_1_1_2 |
| cc1_1_1_3 |
| cc1_1_2 |
| cc1_1_2_1 |
| cc1_1_2_2 |
| cc1_1_2_3 |
| cc1_1_3 |
| cc1_1_3_1 |
| cc1_1_3_2 |
| cc1_1_3_3 |
| cc1_2 |
| cc1_2_1 |
| cc1_2_1_1 |
| cc1_2_1_2 |
| cc1_2_1_3 |
| cc1_2_2 |
| cc1_2_2_1 |
| cc1_2_2_2 |
| cc1_2_2_3 |
| cc1_2_3 |
| cc1_2_3_1 |
| cc1_2_3_2 |
| cc1_2_3_3 |
| cc1_3 |
| cc1_3_1 |
| cc1_3_1_1 |
| cc1_3_1_2 |
| cc1_3_1_3 |
| cc1_3_2 |
| cc1_3_2_1 |
| cc1_3_2_2 |
| cc1_3_2_3 |
| cc1_3_3 |
| cc1_3_3_1 |
| cc1_3_3_2 |
| cc1_3_3_3 |
| cc2 |
| cc2_1 |
| cc2_1_1 |
| cc2_1_1_1 |
| cc2_1_1_2 |
| cc2_1_1_3 |
| cc2_1_2 |
| cc2_1_2_1 |
| cc2_1_2_2 |
| cc2_1_2_3 |
| cc2_1_3 |
| cc2_1_3_1 |
| cc2_1_3_2 |
| cc2_1_3_3 |
| cc2_2 |
| cc2_2_1 |
| cc2_2_1_1 |
| cc2_2_1_2 |
| cc2_2_1_3 |
| cc2_2_2 |
| cc2_2_2_1 |
| cc2_2_2_2 |
| cc2_2_2_3 |
| cc2_2_3 |
| cc2_2_3_1 |
| cc2_2_3_2 |
| cc2_2_3_3 |
| cc2_3 |
| cc2_3_1 |
| cc2_3_1_1 |
| cc2_3_1_2 |
| cc2_3_1_3 |
| cc2_3_2 |
| cc2_3_2_1 |
| cc2_3_2_2 |
| cc2_3_2_3 |
| cc2_3_3 |
| cc2_3_3_1 |
| cc2_3_3_2 |
| cc2_3_3_3 |
| cc3 |
| cc3_1 |
| cc3_1_1 |
| cc3_1_1_1 |
| cc3_1_1_2 |
| cc3_1_1_3 |
| cc3_1_2 |
| cc3_1_2_1 |
| cc3_1_2_2 |
| cc3_1_2_3 |
| cc3_1_3 |
| cc3_1_3_1 |
| cc3_1_3_2 |
| cc3_1_3_3 |
| cc3_2 |
| cc3_2_1 |
| cc3_2_1_1 |
| cc3_2_1_2 |
| cc3_2_1_3 |
| cc3_2_2 |
| cc3_2_2_1 |
| cc3_2_2_2 |
| cc3_2_2_3 |
| cc3_2_3 |
| cc3_2_3_1 |
| cc3_2_3_2 |
| cc3_2_3_3 |
| cc3_3 |
| cc3_3_1 |
| cc3_3_1_1 |
| cc3_3_1_2 |
| cc3_3_1_3 |
| cc3_3_2 |
| cc3_3_2_1 |
| cc3_3_2_2 |
| cc3_3_2_3 |
| cc3_3_3 |
| cc3_3_3_1 |
| cc3_3_3_2 |
| cc3_3_3_3 |

## cc_parent

The parent of a cost centre. The root cost centre has no row.
Identified by: cc. References: `cc` refers to `cc`; `parent` refers to `cc`.

| cc | parent |
|---|---|
| cc1 | company |
| cc1_1 | cc1 |
| cc1_1_1 | cc1_1 |
| cc1_1_1_1 | cc1_1_1 |
| cc1_1_1_2 | cc1_1_1 |
| cc1_1_1_3 | cc1_1_1 |
| cc1_1_2 | cc1_1 |
| cc1_1_2_1 | cc1_1_2 |
| cc1_1_2_2 | cc1_1_2 |
| cc1_1_2_3 | cc1_1_2 |
| cc1_1_3 | cc1_1 |
| cc1_1_3_1 | cc1_1_3 |
| cc1_1_3_2 | cc1_1_3 |
| cc1_1_3_3 | cc1_1_3 |
| cc1_2 | cc1 |
| cc1_2_1 | cc1_2 |
| cc1_2_1_1 | cc1_2_1 |
| cc1_2_1_2 | cc1_2_1 |
| cc1_2_1_3 | cc1_2_1 |
| cc1_2_2 | cc1_2 |
| cc1_2_2_1 | cc1_2_2 |
| cc1_2_2_2 | cc1_2_2 |
| cc1_2_2_3 | cc1_2_2 |
| cc1_2_3 | cc1_2 |
| cc1_2_3_1 | cc1_2_3 |
| cc1_2_3_2 | cc1_2_3 |
| cc1_2_3_3 | cc1_2_3 |
| cc1_3 | cc1 |
| cc1_3_1 | cc1_3 |
| cc1_3_1_1 | cc1_3_1 |
| cc1_3_1_2 | cc1_3_1 |
| cc1_3_1_3 | cc1_3_1 |
| cc1_3_2 | cc1_3 |
| cc1_3_2_1 | cc1_3_2 |
| cc1_3_2_2 | cc1_3_2 |
| cc1_3_2_3 | cc1_3_2 |
| cc1_3_3 | cc1_3 |
| cc1_3_3_1 | cc1_3_3 |
| cc1_3_3_2 | cc1_3_3 |
| cc1_3_3_3 | cc1_3_3 |
| cc2 | company |
| cc2_1 | cc2 |
| cc2_1_1 | cc2_1 |
| cc2_1_1_1 | cc2_1_1 |
| cc2_1_1_2 | cc2_1_1 |
| cc2_1_1_3 | cc2_1_1 |
| cc2_1_2 | cc2_1 |
| cc2_1_2_1 | cc2_1_2 |
| cc2_1_2_2 | cc2_1_2 |
| cc2_1_2_3 | cc2_1_2 |
| cc2_1_3 | cc2_1 |
| cc2_1_3_1 | cc2_1_3 |
| cc2_1_3_2 | cc2_1_3 |
| cc2_1_3_3 | cc2_1_3 |
| cc2_2 | cc2 |
| cc2_2_1 | cc2_2 |
| cc2_2_1_1 | cc2_2_1 |
| cc2_2_1_2 | cc2_2_1 |
| cc2_2_1_3 | cc2_2_1 |
| cc2_2_2 | cc2_2 |
| cc2_2_2_1 | cc2_2_2 |
| cc2_2_2_2 | cc2_2_2 |
| cc2_2_2_3 | cc2_2_2 |
| cc2_2_3 | cc2_2 |
| cc2_2_3_1 | cc2_2_3 |
| cc2_2_3_2 | cc2_2_3 |
| cc2_2_3_3 | cc2_2_3 |
| cc2_3 | cc2 |
| cc2_3_1 | cc2_3 |
| cc2_3_1_1 | cc2_3_1 |
| cc2_3_1_2 | cc2_3_1 |
| cc2_3_1_3 | cc2_3_1 |
| cc2_3_2 | cc2_3 |
| cc2_3_2_1 | cc2_3_2 |
| cc2_3_2_2 | cc2_3_2 |
| cc2_3_2_3 | cc2_3_2 |
| cc2_3_3 | cc2_3 |
| cc2_3_3_1 | cc2_3_3 |
| cc2_3_3_2 | cc2_3_3 |
| cc2_3_3_3 | cc2_3_3 |
| cc3 | company |
| cc3_1 | cc3 |
| cc3_1_1 | cc3_1 |
| cc3_1_1_1 | cc3_1_1 |
| cc3_1_1_2 | cc3_1_1 |
| cc3_1_1_3 | cc3_1_1 |
| cc3_1_2 | cc3_1 |
| cc3_1_2_1 | cc3_1_2 |
| cc3_1_2_2 | cc3_1_2 |
| cc3_1_2_3 | cc3_1_2 |
| cc3_1_3 | cc3_1 |
| cc3_1_3_1 | cc3_1_3 |
| cc3_1_3_2 | cc3_1_3 |
| cc3_1_3_3 | cc3_1_3 |
| cc3_2 | cc3 |
| cc3_2_1 | cc3_2 |
| cc3_2_1_1 | cc3_2_1 |
| cc3_2_1_2 | cc3_2_1 |
| cc3_2_1_3 | cc3_2_1 |
| cc3_2_2 | cc3_2 |
| cc3_2_2_1 | cc3_2_2 |
| cc3_2_2_2 | cc3_2_2 |
| cc3_2_2_3 | cc3_2_2 |
| cc3_2_3 | cc3_2 |
| cc3_2_3_1 | cc3_2_3 |
| cc3_2_3_2 | cc3_2_3 |
| cc3_2_3_3 | cc3_2_3 |
| cc3_3 | cc3 |
| cc3_3_1 | cc3_3 |
| cc3_3_1_1 | cc3_3_1 |
| cc3_3_1_2 | cc3_3_1 |
| cc3_3_1_3 | cc3_3_1 |
| cc3_3_2 | cc3_3 |
| cc3_3_2_1 | cc3_3_2 |
| cc3_3_2_2 | cc3_3_2 |
| cc3_3_2_3 | cc3_3_2 |
| cc3_3_3 | cc3_3 |
| cc3_3_3_1 | cc3_3_3 |
| cc3_3_3_2 | cc3_3_3 |
| cc3_3_3_3 | cc3_3_3 |

## org_unit

The organisational unit a cost centre belongs to.
Identified by: cc. References: `cc` refers to `cc`.

| cc | unit |
|---|---|
| company | leadership |
| cc1 | leadership |
| cc1_1 | leadership |
| cc1_1_1 | leadership |
| cc1_1_1_1 | support |
| cc1_1_1_2 | delivery |
| cc1_1_1_3 | support |
| cc1_1_2 | leadership |
| cc1_1_2_1 | delivery |
| cc1_1_2_2 | support |
| cc1_1_2_3 | support |
| cc1_1_3 | leadership |
| cc1_1_3_1 | delivery |
| cc1_1_3_2 | support |
| cc1_1_3_3 | support |
| cc1_2 | leadership |
| cc1_2_1 | leadership |
| cc1_2_1_1 | support |
| cc1_2_1_2 | support |
| cc1_2_1_3 | delivery |
| cc1_2_2 | leadership |
| cc1_2_2_1 | support |
| cc1_2_2_2 | support |
| cc1_2_2_3 | support |
| cc1_2_3 | leadership |
| cc1_2_3_1 | support |
| cc1_2_3_2 | support |
| cc1_2_3_3 | delivery |
| cc1_3 | leadership |
| cc1_3_1 | leadership |
| cc1_3_1_1 | delivery |
| cc1_3_1_2 | delivery |
| cc1_3_1_3 | support |
| cc1_3_2 | leadership |
| cc1_3_2_1 | delivery |
| cc1_3_2_2 | support |
| cc1_3_2_3 | support |
| cc1_3_3 | leadership |
| cc1_3_3_1 | delivery |
| cc1_3_3_2 | support |
| cc1_3_3_3 | support |
| cc2 | leadership |
| cc2_1 | leadership |
| cc2_1_1 | leadership |
| cc2_1_1_1 | support |
| cc2_1_1_2 | delivery |
| cc2_1_1_3 | support |
| cc2_1_2 | leadership |
| cc2_1_2_1 | delivery |
| cc2_1_2_2 | delivery |
| cc2_1_2_3 | delivery |
| cc2_1_3 | leadership |
| cc2_1_3_1 | support |
| cc2_1_3_2 | support |
| cc2_1_3_3 | support |
| cc2_2 | leadership |
| cc2_2_1 | leadership |
| cc2_2_1_1 | support |
| cc2_2_1_2 | delivery |
| cc2_2_1_3 | support |
| cc2_2_2 | leadership |
| cc2_2_2_1 | delivery |
| cc2_2_2_2 | delivery |
| cc2_2_2_3 | delivery |
| cc2_2_3 | leadership |
| cc2_2_3_1 | support |
| cc2_2_3_2 | support |
| cc2_2_3_3 | support |
| cc2_3 | leadership |
| cc2_3_1 | leadership |
| cc2_3_1_1 | support |
| cc2_3_1_2 | delivery |
| cc2_3_1_3 | delivery |
| cc2_3_2 | leadership |
| cc2_3_2_1 | support |
| cc2_3_2_2 | support |
| cc2_3_2_3 | support |
| cc2_3_3 | leadership |
| cc2_3_3_1 | delivery |
| cc2_3_3_2 | support |
| cc2_3_3_3 | delivery |
| cc3 | leadership |
| cc3_1 | leadership |
| cc3_1_1 | leadership |
| cc3_1_1_1 | support |
| cc3_1_1_2 | support |
| cc3_1_1_3 | delivery |
| cc3_1_2 | leadership |
| cc3_1_2_1 | support |
| cc3_1_2_2 | support |
| cc3_1_2_3 | support |
| cc3_1_3 | leadership |
| cc3_1_3_1 | support |
| cc3_1_3_2 | delivery |
| cc3_1_3_3 | support |
| cc3_2 | leadership |
| cc3_2_1 | leadership |
| cc3_2_1_1 | delivery |
| cc3_2_1_2 | support |
| cc3_2_1_3 | support |
| cc3_2_2 | leadership |
| cc3_2_2_1 | delivery |
| cc3_2_2_2 | support |
| cc3_2_2_3 | support |
| cc3_2_3 | leadership |
| cc3_2_3_1 | delivery |
| cc3_2_3_2 | support |
| cc3_2_3_3 | delivery |
| cc3_3 | leadership |
| cc3_3_1 | leadership |
| cc3_3_1_1 | support |
| cc3_3_1_2 | support |
| cc3_3_1_3 | support |
| cc3_3_2 | leadership |
| cc3_3_2_1 | support |
| cc3_3_2_2 | delivery |
| cc3_3_2_3 | delivery |
| cc3_3_3 | leadership |
| cc3_3_3_1 | delivery |
| cc3_3_3_2 | delivery |
| cc3_3_3_3 | delivery |

## emp

An employee, their role, and their current cost centre as finance records it.
Identified by: emp. References: `cc` refers to `cc`.

| emp | role | cc |
|---|---|---|
| e000 | vp | company |
| e001 | director | cc1 |
| e002 | senior_manager | cc1_1 |
| e003 | senior_manager | cc1_1_1 |
| e004 | manager | cc1_1_1_1 |
| e005 | manager | cc1_1_1_2 |
| e006 | manager | cc1_1_1_3 |
| e007 | senior_manager | cc1_1_2 |
| e008 | manager | cc1_1_2_1 |
| e009 | manager | cc1_1_2_2 |
| e010 | manager | cc1_1_2_3 |
| e011 | senior_manager | cc1_1_3 |
| e012 | manager | cc1_1_3_1 |
| e013 | manager | cc1_1_3_2 |
| e014 | manager | cc1_1_3_3 |
| e015 | senior_manager | cc1_2 |
| e016 | senior_manager | cc1_2_1 |
| e017 | manager | cc1_2_1_1 |
| e018 | manager | cc1_2_1_2 |
| e019 | manager | cc1_2_1_3 |
| e020 | senior_manager | cc1_2_2 |
| e021 | manager | cc1_2_2_1 |
| e022 | manager | cc1_2_2_2 |
| e023 | manager | cc1_2_2_3 |
| e024 | senior_manager | cc1_2_3 |
| e025 | manager | cc1_2_3_1 |
| e026 | manager | cc1_2_3_2 |
| e027 | manager | cc1_2_3_3 |
| e028 | senior_manager | cc1_3 |
| e029 | senior_manager | cc1_3_1 |
| e030 | manager | cc1_3_1_1 |
| e031 | manager | cc1_3_1_2 |
| e032 | manager | cc1_3_1_3 |
| e033 | senior_manager | cc1_3_2 |
| e034 | manager | cc1_3_2_1 |
| e035 | manager | cc1_3_2_2 |
| e036 | manager | cc1_3_2_3 |
| e037 | senior_manager | cc1_3_3 |
| e038 | manager | cc1_3_3_1 |
| e039 | manager | cc1_3_3_2 |
| e040 | manager | cc1_3_3_3 |
| e041 | director | cc2 |
| e042 | senior_manager | cc2_1 |
| e043 | senior_manager | cc2_1_1 |
| e044 | manager | cc2_1_1_1 |
| e045 | manager | cc2_1_1_2 |
| e046 | manager | cc2_1_1_3 |
| e047 | senior_manager | cc2_1_2 |
| e048 | manager | cc2_1_2_1 |
| e049 | manager | cc2_1_2_2 |
| e050 | manager | cc2_1_2_3 |
| e051 | senior_manager | cc2_1_3 |
| e052 | manager | cc2_1_3_1 |
| e053 | manager | cc2_1_3_2 |
| e054 | manager | cc2_1_3_3 |
| e055 | senior_manager | cc2_2 |
| e056 | senior_manager | cc2_2_1 |
| e057 | manager | cc2_2_1_1 |
| e058 | manager | cc2_2_1_2 |
| e059 | manager | cc2_2_1_3 |
| e060 | senior_manager | cc2_2_2 |
| e061 | manager | cc2_2_2_1 |
| e062 | manager | cc2_2_2_2 |
| e063 | manager | cc2_2_2_3 |
| e064 | senior_manager | cc2_2_3 |
| e065 | manager | cc2_2_3_1 |
| e066 | manager | cc2_2_3_2 |
| e067 | manager | cc2_2_3_3 |
| e068 | senior_manager | cc2_3 |
| e069 | senior_manager | cc2_3_1 |
| e070 | manager | cc2_3_1_1 |
| e071 | manager | cc2_3_1_2 |
| e072 | manager | cc2_3_1_3 |
| e073 | senior_manager | cc2_3_2 |
| e074 | manager | cc2_3_2_1 |
| e075 | manager | cc2_3_2_2 |
| e076 | manager | cc2_3_2_3 |
| e077 | senior_manager | cc2_3_3 |
| e078 | manager | cc2_3_3_1 |
| e079 | manager | cc2_3_3_2 |
| e080 | manager | cc2_3_3_3 |
| e081 | director | cc3 |
| e082 | senior_manager | cc3_1 |
| e083 | senior_manager | cc3_1_1 |
| e084 | manager | cc3_1_1_1 |
| e085 | manager | cc3_1_1_2 |
| e086 | manager | cc3_1_1_3 |
| e087 | senior_manager | cc3_1_2 |
| e088 | manager | cc3_1_2_1 |
| e089 | manager | cc3_1_2_2 |
| e090 | manager | cc3_1_2_3 |
| e091 | senior_manager | cc3_1_3 |
| e092 | manager | cc3_1_3_1 |
| e093 | manager | cc3_1_3_2 |
| e094 | manager | cc3_1_3_3 |
| e095 | senior_manager | cc3_2 |
| e096 | senior_manager | cc3_2_1 |
| e097 | manager | cc3_2_1_1 |
| e098 | manager | cc3_2_1_2 |
| e099 | manager | cc3_2_1_3 |
| e100 | senior_manager | cc3_2_2 |
| e101 | manager | cc3_2_2_1 |
| e102 | manager | cc3_2_2_2 |
| e103 | manager | cc3_2_2_3 |
| e104 | senior_manager | cc3_2_3 |
| e105 | manager | cc3_2_3_1 |
| e106 | manager | cc3_2_3_2 |
| e107 | manager | cc3_2_3_3 |
| e108 | senior_manager | cc3_3 |
| e109 | senior_manager | cc3_3_1 |
| e110 | manager | cc3_3_1_1 |
| e111 | manager | cc3_3_1_2 |
| e112 | manager | cc3_3_1_3 |
| e113 | senior_manager | cc3_3_2 |
| e114 | manager | cc3_3_2_1 |
| e115 | manager | cc3_3_2_2 |
| e116 | manager | cc3_3_2_3 |
| e117 | senior_manager | cc3_3_3 |
| e118 | manager | cc3_3_3_1 |
| e119 | manager | cc3_3_3_2 |
| e120 | manager | cc3_3_3_3 |
| e121 | analyst | cc1_1_1_1 |
| e122 | analyst | cc1_1_1_1 |
| e123 | analyst | cc1_1_1_2 |
| e124 | analyst | cc1_1_1_2 |
| e125 | analyst | cc1_1_1_3 |
| e126 | analyst | cc3_3_3_3 |
| e127 | analyst | cc1_1_2_1 |
| e128 | analyst | cc1_1_2_1 |
| e129 | analyst | cc1_1_2_2 |
| e130 | analyst | cc1_1_2_2 |
| e131 | analyst | cc1_1_2_3 |
| e132 | analyst | cc1_1_2_3 |
| e133 | analyst | cc1_1_3_1 |
| e134 | analyst | cc1_1_3_1 |
| e135 | analyst | cc1_1_3_2 |
| e136 | analyst | cc1_1_3_2 |
| e137 | analyst | cc1_1_3_3 |
| e138 | analyst | cc1_1_3_3 |
| e139 | analyst | cc1_2_1_1 |
| e140 | analyst | cc1_2_1_1 |
| e141 | analyst | cc1_2_1_2 |
| e142 | analyst | cc1_2_1_2 |
| e143 | analyst | cc1_2_1_3 |
| e144 | analyst | cc1_2_1_3 |
| e145 | analyst | cc1_2_2_1 |
| e146 | analyst | cc1_2_2_1 |
| e147 | analyst | cc1_2_2_2 |
| e148 | analyst | cc1_2_2_2 |
| e149 | analyst | cc1_2_2_3 |
| e150 | analyst | cc1_2_2_3 |
| e151 | analyst | cc1_2_3_1 |
| e152 | analyst | cc1_2_3_1 |
| e153 | analyst | cc1_2_3_2 |
| e154 | analyst | cc1_2_3_2 |
| e155 | analyst | cc1_2_3_3 |
| e156 | analyst | cc1_2_3_3 |
| e157 | analyst | cc1_3_1_1 |
| e158 | analyst | cc1_3_1_1 |
| e159 | analyst | cc1_3_1_2 |
| e160 | analyst | cc1_3_1_2 |
| e161 | analyst | cc1_3_1_3 |
| e162 | analyst | cc1_3_1_3 |
| e163 | analyst | cc1_3_2_1 |
| e164 | analyst | cc1_3_2_1 |
| e165 | analyst | cc1_3_2_2 |
| e166 | analyst | cc1_3_2_2 |
| e167 | analyst | cc1_3_2_3 |
| e168 | analyst | cc1_3_2_3 |
| e169 | analyst | cc1_3_3_1 |
| e170 | analyst | cc1_3_3_1 |
| e171 | analyst | cc1_3_3_2 |
| e172 | analyst | cc1_3_3_2 |
| e173 | analyst | cc3_2_1_2 |
| e174 | analyst | cc1_3_3_3 |
| e175 | analyst | cc2_1_1_1 |
| e176 | analyst | cc2_1_1_1 |
| e177 | analyst | cc2_1_1_2 |
| e178 | analyst | cc2_1_1_2 |
| e179 | analyst | cc2_1_1_3 |
| e180 | analyst | cc2_1_1_3 |
| e181 | analyst | cc2_1_2_1 |
| e182 | analyst | cc2_1_2_1 |
| e183 | analyst | cc2_1_2_2 |
| e184 | analyst | cc2_1_2_2 |
| e185 | analyst | cc2_1_2_3 |
| e186 | analyst | cc2_1_2_3 |
| e187 | analyst | cc2_1_3_1 |
| e188 | analyst | cc2_1_3_1 |
| e189 | analyst | cc2_1_3_2 |
| e190 | analyst | cc2_1_3_2 |
| e191 | analyst | cc2_1_3_3 |
| e192 | analyst | cc2_1_3_3 |
| e193 | analyst | cc3_2_3_2 |
| e194 | analyst | cc2_2_1_1 |
| e195 | analyst | cc2_2_1_2 |
| e196 | analyst | cc2_2_1_2 |
| e197 | analyst | cc2_2_1_3 |
| e198 | analyst | cc1_3_2_2 |
| e199 | analyst | cc2_2_2_1 |
| e200 | analyst | cc2_2_2_1 |
| e201 | analyst | cc2_2_2_2 |
| e202 | analyst | cc2_2_2_2 |
| e203 | analyst | cc2_2_2_3 |
| e204 | analyst | cc2_2_2_3 |
| e205 | analyst | cc2_2_3_1 |
| e206 | analyst | cc2_2_3_1 |
| e207 | analyst | cc2_2_3_2 |
| e208 | analyst | cc2_2_3_2 |
| e209 | analyst | cc2_2_3_3 |
| e210 | analyst | cc2_2_3_3 |
| e211 | analyst | cc2_3_1_1 |
| e212 | analyst | cc2_3_1_1 |
| e213 | analyst | cc2_1_3_1 |
| e214 | analyst | cc2_3_1_2 |
| e215 | analyst | cc2_3_1_3 |
| e216 | analyst | cc2_3_1_3 |
| e217 | analyst | cc2_3_2_1 |
| e218 | analyst | cc2_3_2_1 |
| e219 | analyst | cc2_3_2_2 |
| e220 | analyst | cc2_3_2_2 |
| e221 | analyst | cc2_3_2_3 |
| e222 | analyst | cc2_3_2_3 |
| e223 | analyst | cc2_3_3_1 |
| e224 | analyst | cc2_3_3_1 |
| e225 | analyst | cc2_3_3_2 |
| e226 | analyst | cc2_3_3_2 |
| e227 | analyst | cc2_3_3_3 |
| e228 | analyst | cc2_3_3_3 |
| e229 | analyst | cc2_3_2_3 |
| e230 | analyst | cc3_1_1_1 |
| e231 | analyst | cc3_1_1_2 |
| e232 | analyst | cc3_1_1_2 |
| e233 | analyst | cc3_1_1_3 |
| e234 | analyst | cc3_1_1_3 |
| e235 | analyst | cc3_1_2_1 |
| e236 | analyst | cc3_1_2_1 |
| e237 | analyst | cc3_1_2_2 |
| e238 | analyst | cc3_1_2_2 |
| e239 | analyst | cc3_1_2_3 |
| e240 | analyst | cc3_1_2_3 |
| e241 | analyst | cc3_1_3_1 |
| e242 | analyst | cc3_1_3_1 |
| e243 | analyst | cc3_1_3_2 |
| e244 | analyst | cc3_1_3_2 |
| e245 | analyst | cc3_1_3_3 |
| e246 | analyst | cc3_1_3_3 |
| e247 | analyst | cc3_2_1_1 |
| e248 | analyst | cc3_2_1_1 |
| e249 | analyst | cc3_2_1_2 |
| e250 | analyst | cc3_2_1_2 |
| e251 | analyst | cc3_2_1_3 |
| e252 | analyst | cc3_2_1_3 |
| e253 | analyst | cc3_2_2_1 |
| e254 | analyst | cc3_2_2_1 |
| e255 | analyst | cc3_2_2_2 |
| e256 | analyst | cc3_2_2_2 |
| e257 | analyst | cc3_2_2_3 |
| e258 | analyst | cc3_2_2_3 |
| e259 | analyst | cc3_2_3_1 |
| e260 | analyst | cc3_2_3_1 |
| e261 | analyst | cc3_2_3_2 |
| e262 | analyst | cc3_2_3_2 |
| e263 | analyst | cc3_2_3_3 |
| e264 | analyst | cc3_2_3_3 |
| e265 | analyst | cc3_2_2_3 |
| e266 | analyst | cc3_3_1_1 |
| e267 | analyst | cc3_3_1_2 |
| e268 | analyst | cc3_3_1_2 |
| e269 | analyst | cc3_3_1_3 |
| e270 | analyst | cc3_3_1_3 |
| e271 | analyst | cc3_3_2_1 |
| e272 | analyst | cc3_3_2_1 |
| e273 | analyst | cc3_3_2_2 |
| e274 | analyst | cc3_3_2_2 |
| e275 | analyst | cc3_3_2_3 |
| e276 | analyst | cc3_3_2_3 |
| e277 | analyst | cc3_3_3_1 |
| e278 | analyst | cc3_3_3_1 |
| e279 | analyst | cc3_3_3_2 |
| e280 | analyst | cc3_3_3_2 |
| e281 | analyst | cc3_3_3_3 |
| e282 | analyst | cc3_3_3_3 |

## reports

An employee's direct manager.
Identified by: emp. References: `emp` refers to `emp`; `manager` refers to `emp`.

| emp | manager |
|---|---|
| e001 | e000 |
| e002 | e001 |
| e003 | e002 |
| e004 | e003 |
| e005 | e003 |
| e006 | e003 |
| e007 | e002 |
| e008 | e007 |
| e009 | e007 |
| e010 | e007 |
| e011 | e002 |
| e012 | e011 |
| e013 | e011 |
| e014 | e011 |
| e015 | e001 |
| e016 | e015 |
| e017 | e016 |
| e018 | e016 |
| e019 | e016 |
| e020 | e015 |
| e021 | e020 |
| e022 | e020 |
| e023 | e020 |
| e024 | e015 |
| e025 | e024 |
| e026 | e024 |
| e027 | e024 |
| e028 | e001 |
| e029 | e028 |
| e030 | e029 |
| e031 | e029 |
| e032 | e029 |
| e033 | e028 |
| e034 | e033 |
| e035 | e033 |
| e036 | e033 |
| e037 | e028 |
| e038 | e037 |
| e039 | e037 |
| e040 | e037 |
| e041 | e000 |
| e042 | e041 |
| e043 | e042 |
| e044 | e043 |
| e045 | e043 |
| e046 | e043 |
| e047 | e042 |
| e048 | e047 |
| e049 | e047 |
| e050 | e047 |
| e051 | e042 |
| e052 | e051 |
| e053 | e051 |
| e054 | e051 |
| e055 | e041 |
| e056 | e055 |
| e057 | e056 |
| e058 | e056 |
| e059 | e056 |
| e060 | e055 |
| e061 | e060 |
| e062 | e060 |
| e063 | e060 |
| e064 | e055 |
| e065 | e064 |
| e066 | e064 |
| e067 | e064 |
| e068 | e041 |
| e069 | e068 |
| e070 | e069 |
| e071 | e069 |
| e072 | e069 |
| e073 | e068 |
| e074 | e073 |
| e075 | e073 |
| e076 | e073 |
| e077 | e068 |
| e078 | e077 |
| e079 | e077 |
| e080 | e077 |
| e081 | e000 |
| e082 | e081 |
| e083 | e082 |
| e084 | e083 |
| e085 | e083 |
| e086 | e083 |
| e087 | e082 |
| e088 | e087 |
| e089 | e087 |
| e090 | e087 |
| e091 | e082 |
| e092 | e091 |
| e093 | e091 |
| e094 | e091 |
| e095 | e081 |
| e096 | e095 |
| e097 | e096 |
| e098 | e096 |
| e099 | e096 |
| e100 | e095 |
| e101 | e100 |
| e102 | e100 |
| e103 | e100 |
| e104 | e095 |
| e105 | e104 |
| e106 | e104 |
| e107 | e104 |
| e108 | e081 |
| e109 | e108 |
| e110 | e109 |
| e111 | e109 |
| e112 | e109 |
| e113 | e108 |
| e114 | e113 |
| e115 | e113 |
| e116 | e113 |
| e117 | e108 |
| e118 | e117 |
| e119 | e117 |
| e120 | e117 |
| e121 | e004 |
| e122 | e004 |
| e123 | e005 |
| e124 | e005 |
| e125 | e006 |
| e126 | e120 |
| e127 | e008 |
| e128 | e008 |
| e129 | e009 |
| e130 | e009 |
| e131 | e010 |
| e132 | e010 |
| e133 | e012 |
| e134 | e012 |
| e135 | e013 |
| e136 | e013 |
| e137 | e014 |
| e138 | e014 |
| e139 | e017 |
| e140 | e017 |
| e141 | e018 |
| e142 | e018 |
| e143 | e019 |
| e144 | e019 |
| e145 | e021 |
| e146 | e021 |
| e147 | e022 |
| e148 | e022 |
| e149 | e023 |
| e150 | e023 |
| e151 | e025 |
| e152 | e025 |
| e153 | e026 |
| e154 | e026 |
| e155 | e027 |
| e156 | e027 |
| e157 | e030 |
| e158 | e030 |
| e159 | e031 |
| e160 | e031 |
| e161 | e032 |
| e162 | e032 |
| e163 | e034 |
| e164 | e034 |
| e165 | e035 |
| e166 | e035 |
| e167 | e036 |
| e168 | e036 |
| e169 | e038 |
| e170 | e038 |
| e171 | e039 |
| e172 | e039 |
| e173 | e098 |
| e174 | e040 |
| e175 | e044 |
| e176 | e044 |
| e177 | e045 |
| e178 | e045 |
| e179 | e046 |
| e180 | e046 |
| e181 | e048 |
| e182 | e048 |
| e183 | e049 |
| e184 | e049 |
| e185 | e050 |
| e186 | e050 |
| e187 | e052 |
| e188 | e052 |
| e189 | e053 |
| e190 | e053 |
| e191 | e054 |
| e192 | e054 |
| e193 | e106 |
| e194 | e057 |
| e195 | e058 |
| e196 | e058 |
| e197 | e059 |
| e198 | e035 |
| e199 | e061 |
| e200 | e061 |
| e201 | e062 |
| e202 | e062 |
| e203 | e063 |
| e204 | e063 |
| e205 | e065 |
| e206 | e065 |
| e207 | e066 |
| e208 | e066 |
| e209 | e067 |
| e210 | e067 |
| e211 | e070 |
| e212 | e070 |
| e213 | e052 |
| e214 | e071 |
| e215 | e072 |
| e216 | e072 |
| e217 | e074 |
| e218 | e074 |
| e219 | e075 |
| e220 | e075 |
| e221 | e076 |
| e222 | e076 |
| e223 | e078 |
| e224 | e078 |
| e225 | e079 |
| e226 | e079 |
| e227 | e080 |
| e228 | e080 |
| e229 | e076 |
| e230 | e084 |
| e231 | e085 |
| e232 | e085 |
| e233 | e086 |
| e234 | e086 |
| e235 | e088 |
| e236 | e088 |
| e237 | e089 |
| e238 | e089 |
| e239 | e090 |
| e240 | e090 |
| e241 | e092 |
| e242 | e092 |
| e243 | e093 |
| e244 | e093 |
| e245 | e094 |
| e246 | e094 |
| e247 | e097 |
| e248 | e097 |
| e249 | e098 |
| e250 | e098 |
| e251 | e099 |
| e252 | e099 |
| e253 | e101 |
| e254 | e101 |
| e255 | e102 |
| e256 | e102 |
| e257 | e103 |
| e258 | e103 |
| e259 | e105 |
| e260 | e105 |
| e261 | e106 |
| e262 | e106 |
| e263 | e107 |
| e264 | e107 |
| e265 | e103 |
| e266 | e110 |
| e267 | e111 |
| e268 | e111 |
| e269 | e112 |
| e270 | e112 |
| e271 | e114 |
| e272 | e114 |
| e273 | e115 |
| e274 | e115 |
| e275 | e116 |
| e276 | e116 |
| e277 | e118 |
| e278 | e118 |
| e279 | e119 |
| e280 | e119 |
| e281 | e120 |
| e282 | e120 |

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
| r001 | e090 | 8000 | services | acme | 2026-06-03 | pending |
| r002 | e105 | 20000 | software | cog | 2026-08-02 | pending |
| r003 | e028 | 20000 | software | dyne | 2026-09-10 | pending |
| r004 | e253 | 12000 | capital | cog | 2026-09-14 | pending |
| r005 | e035 | 90000 | hardware | dyne | 2026-09-05 | pending |
| r006 | e118 | 45000 | hardware | bolt | 2026-06-05 | pending |
| r007 | e038 | 90000 | software | edge | 2026-06-09 | pending |
| r008 | e040 | 20000 | capital | cog | 2026-09-13 | cancelled |
| r009 | e145 | 12000 | capital | bolt | 2026-07-12 | pending |
| r010 | e264 | 60000 | hardware | cog | 2026-09-08 | pending |
| r011 | e136 | 120000 | services | bolt | 2026-08-25 | pending |
| r012 | e179 | 12000 | hardware | dyne | 2026-09-15 | pending |
| r013 | e214 | 3000 | capital | edge | 2026-08-20 | pending |
| r014 | e233 | 12000 | services | cog | 2026-06-28 | pending |
| r015 | e019 | 30000 | capital | dyne | 2026-09-13 | pending |
| r016 | e204 | 90000 | software | cog | 2026-07-07 | pending |
| r017 | e143 | 45000 | services | acme | 2026-07-28 | pending |
| r018 | e054 | 8000 | software | acme | 2026-06-14 | pending |
| r019 | e216 | 30000 | services | fern | 2026-07-31 | pending |
| r020 | e250 | 90000 | hardware | bolt | 2026-06-17 | pending |
| r021 | e264 | 38000 | software | bolt | 2026-07-27 | pending |
| r022 | e068 | 38000 | capital | dyne | 2026-09-06 | pending |
| r023 | e026 | 38000 | capital | dyne | 2026-08-10 | pending |
| r024 | e147 | 38000 | software | bolt | 2026-09-01 | pending |
| r025 | e125 | 38000 | hardware | fern | 2026-09-03 | pending |
| r026 | e254 | 12000 | hardware | fern | 2026-06-18 | pending |
| r027 | e169 | 3000 | software | fern | 2026-07-23 | pending |
| r028 | e117 | 20000 | software | bolt | 2026-07-11 | pending |
| r029 | e201 | 12000 | services | edge | 2026-07-21 | pending |
| r030 | e080 | 45000 | capital | edge | 2026-08-12 | pending |
| r031 | e192 | 38000 | services | edge | 2026-07-20 | pending |
| r032 | e097 | 12000 | software | edge | 2026-08-15 | pending |
| r033 | e249 | 30000 | hardware | acme | 2026-08-30 | pending |
| r034 | e160 | 45000 | hardware | acme | 2026-06-09 | pending |
| r035 | e051 | 30000 | services | fern | 2026-08-02 | pending |
| r036 | e091 | 8000 | services | fern | 2026-08-17 | pending |
| r037 | e279 | 8000 | services | fern | 2026-07-20 | pending |
| r038 | e096 | 20000 | hardware | dyne | 2026-08-25 | pending |
| r039 | e055 | 12000 | hardware | cog | 2026-09-14 | pending |
| r040 | e044 | 20000 | software | cog | 2026-06-26 | pending |
| r041 | e081 | 90000 | capital | bolt | 2026-08-17 | pending |
| r042 | e176 | 12000 | capital | fern | 2026-07-12 | pending |
| r043 | e107 | 20000 | services | fern | 2026-08-31 | pending |
| r044 | e203 | 120000 | capital | acme | 2026-08-22 | pending |
| r045 | e183 | 20000 | hardware | cog | 2026-06-24 | pending |
| r046 | e264 | 30000 | capital | cog | 2026-06-22 | pending |
| r047 | e201 | 8000 | hardware | edge | 2026-07-11 | cancelled |
| r048 | e151 | 20000 | hardware | dyne | 2026-06-09 | pending |
| r049 | e269 | 3000 | hardware | fern | 2026-08-13 | pending |
| r050 | e110 | 60000 | capital | fern | 2026-08-22 | pending |
| r051 | e100 | 45000 | software | cog | 2026-06-27 | pending |
| r052 | e211 | 20000 | hardware | dyne | 2026-08-20 | pending |
| r053 | e007 | 12000 | hardware | acme | 2026-07-22 | pending |
| r054 | e203 | 60000 | software | cog | 2026-09-10 | pending |
| r055 | e198 | 12000 | services | edge | 2026-07-04 | pending |
| r056 | e108 | 3000 | software | cog | 2026-07-23 | pending |
| r057 | e097 | 30000 | services | acme | 2026-07-06 | pending |
| r058 | e116 | 120000 | hardware | acme | 2026-06-01 | pending |
| r059 | e168 | 8000 | software | dyne | 2026-07-19 | pending |
| r060 | e076 | 8000 | services | dyne | 2026-08-28 | pending |
| r061 | e282 | 60000 | services | acme | 2026-08-04 | cancelled |
| r062 | e007 | 90000 | software | dyne | 2026-08-28 | pending |
| r063 | e269 | 120000 | services | edge | 2026-07-13 | pending |
| r064 | e118 | 38000 | services | dyne | 2026-06-19 | pending |
| r065 | e234 | 120000 | services | dyne | 2026-06-17 | pending |
| r066 | e032 | 120000 | software | fern | 2026-07-19 | pending |
| r067 | e055 | 120000 | capital | cog | 2026-08-30 | pending |
| r068 | e035 | 60000 | hardware | cog | 2026-07-22 | pending |
| r069 | e117 | 60000 | services | bolt | 2026-07-09 | pending |
| r070 | e087 | 120000 | hardware | acme | 2026-06-20 | pending |
| r071 | e133 | 12000 | capital | cog | 2026-07-09 | cancelled |
| r072 | e033 | 38000 | services | acme | 2026-07-10 | pending |
| r073 | e013 | 120000 | services | bolt | 2026-06-20 | pending |
| r074 | e081 | 20000 | hardware | edge | 2026-06-28 | pending |
| r075 | e254 | 60000 | hardware | acme | 2026-06-14 | pending |
| r076 | e150 | 20000 | services | cog | 2026-08-30 | pending |
| r077 | e230 | 8000 | capital | dyne | 2026-06-06 | pending |
| r078 | e164 | 3000 | software | cog | 2026-07-20 | pending |
| r079 | e040 | 8000 | software | bolt | 2026-08-25 | pending |
| r080 | e070 | 3000 | hardware | edge | 2026-07-18 | pending |
| r081 | e072 | 38000 | services | acme | 2026-08-10 | pending |
| r082 | e128 | 3000 | hardware | acme | 2026-07-06 | pending |
| r083 | e132 | 60000 | hardware | acme | 2026-08-22 | pending |
| r084 | e264 | 60000 | software | dyne | 2026-09-05 | pending |
| r085 | e192 | 38000 | services | acme | 2026-07-26 | pending |
| r086 | e273 | 20000 | software | cog | 2026-07-28 | pending |
| r087 | e003 | 12000 | services | edge | 2026-09-08 | pending |
| r088 | e270 | 60000 | capital | acme | 2026-08-31 | pending |
| r089 | e271 | 90000 | hardware | edge | 2026-06-26 | pending |
| r090 | e115 | 120000 | software | fern | 2026-07-15 | pending |
| r091 | e046 | 120000 | services | bolt | 2026-08-22 | pending |
| r092 | e120 | 3000 | hardware | fern | 2026-08-10 | pending |
| r093 | e182 | 90000 | software | edge | 2026-09-12 | pending |
| r094 | e142 | 12000 | capital | cog | 2026-09-08 | pending |
| r095 | e258 | 60000 | software | acme | 2026-07-13 | pending |
| r096 | e219 | 120000 | software | edge | 2026-09-14 | pending |
| r097 | e120 | 38000 | software | fern | 2026-08-20 | pending |
| r098 | e204 | 120000 | services | acme | 2026-06-02 | pending |
| r099 | e139 | 45000 | hardware | edge | 2026-08-16 | pending |
| r100 | e244 | 20000 | software | edge | 2026-06-22 | pending |
| r101 | e047 | 20000 | hardware | edge | 2026-08-05 | pending |
| r102 | e198 | 38000 | software | cog | 2026-07-23 | pending |
| r103 | e016 | 12000 | capital | dyne | 2026-08-04 | pending |
| r104 | e154 | 3000 | software | acme | 2026-06-06 | pending |
| r105 | e221 | 20000 | software | dyne | 2026-06-24 | pending |
| r106 | e105 | 30000 | capital | edge | 2026-06-01 | pending |
| r107 | e032 | 60000 | capital | acme | 2026-08-04 | pending |
| r108 | e279 | 38000 | hardware | edge | 2026-08-21 | cancelled |
| r109 | e230 | 38000 | hardware | dyne | 2026-08-02 | pending |
| r110 | e259 | 38000 | software | edge | 2026-08-04 | pending |
| r111 | e091 | 12000 | services | cog | 2026-07-27 | pending |
| r112 | e003 | 60000 | hardware | bolt | 2026-06-06 | pending |
| r113 | e174 | 90000 | software | edge | 2026-06-07 | pending |
| r114 | e263 | 90000 | services | edge | 2026-08-01 | pending |
| r115 | e161 | 90000 | software | acme | 2026-08-09 | pending |
| r116 | e240 | 38000 | capital | edge | 2026-06-13 | pending |
| r117 | e240 | 45000 | services | edge | 2026-06-19 | pending |
| r118 | e029 | 38000 | software | dyne | 2026-08-10 | pending |
| r119 | e270 | 120000 | hardware | acme | 2026-08-30 | pending |
| r120 | e278 | 38000 | services | acme | 2026-06-14 | pending |
| r121 | e113 | 3000 | software | bolt | 2026-06-25 | pending |
| r122 | e209 | 12000 | software | fern | 2026-06-20 | pending |
| r123 | e127 | 20000 | hardware | edge | 2026-06-07 | pending |
| r124 | e184 | 90000 | hardware | edge | 2026-07-18 | pending |
| r125 | e173 | 30000 | software | fern | 2026-07-13 | pending |
| r126 | e222 | 60000 | capital | bolt | 2026-08-07 | pending |
| r127 | e040 | 38000 | services | acme | 2026-07-10 | pending |
| r128 | e071 | 12000 | capital | bolt | 2026-07-30 | pending |
| r129 | e111 | 8000 | capital | bolt | 2026-09-02 | pending |
| r130 | e222 | 90000 | hardware | acme | 2026-07-06 | cancelled |
| r131 | e097 | 12000 | software | acme | 2026-08-26 | pending |
| r132 | e052 | 30000 | capital | dyne | 2026-09-01 | pending |
| r133 | e267 | 90000 | services | fern | 2026-06-16 | pending |
| r134 | e084 | 3000 | services | dyne | 2026-09-13 | pending |
| r135 | e199 | 12000 | hardware | bolt | 2026-08-09 | pending |
| r136 | e118 | 20000 | hardware | cog | 2026-09-07 | pending |
| r137 | e075 | 90000 | capital | fern | 2026-06-18 | pending |
| r138 | e038 | 20000 | services | bolt | 2026-06-09 | pending |
| r139 | e061 | 90000 | software | dyne | 2026-06-23 | pending |
| r140 | e191 | 90000 | capital | fern | 2026-07-10 | pending |
| r141 | e206 | 120000 | software | cog | 2026-07-05 | cancelled |
| r142 | e163 | 60000 | hardware | fern | 2026-08-27 | cancelled |
| r143 | e271 | 30000 | services | cog | 2026-07-18 | pending |
| r144 | e049 | 60000 | capital | dyne | 2026-07-23 | pending |
| r145 | e197 | 8000 | capital | edge | 2026-08-31 | pending |
| r146 | e072 | 60000 | hardware | edge | 2026-07-12 | pending |
| r147 | e144 | 60000 | software | edge | 2026-08-02 | pending |
| r148 | e278 | 8000 | capital | edge | 2026-07-10 | pending |
| r149 | e076 | 20000 | capital | bolt | 2026-07-07 | pending |
| r150 | e100 | 45000 | services | bolt | 2026-07-10 | cancelled |
| r151 | e230 | 20000 | hardware | bolt | 2026-06-10 | pending |
| r152 | e005 | 8000 | hardware | dyne | 2026-06-14 | pending |
| r153 | e122 | 90000 | capital | bolt | 2026-06-25 | pending |
| r154 | e138 | 20000 | capital | acme | 2026-06-09 | pending |
| r155 | e200 | 12000 | hardware | bolt | 2026-09-08 | pending |
| r156 | e044 | 20000 | capital | cog | 2026-07-05 | pending |
| r157 | e188 | 60000 | hardware | fern | 2026-08-07 | pending |
| r158 | e100 | 90000 | hardware | fern | 2026-07-19 | pending |
| r159 | e229 | 3000 | services | acme | 2026-06-12 | pending |
| r160 | e046 | 3000 | software | acme | 2026-06-15 | pending |
| r161 | e222 | 20000 | hardware | bolt | 2026-06-17 | pending |
| r162 | e077 | 90000 | capital | cog | 2026-07-10 | pending |
| r163 | e207 | 3000 | capital | bolt | 2026-07-05 | pending |
| r164 | e127 | 38000 | hardware | cog | 2026-08-14 | pending |
| r165 | e268 | 120000 | software | edge | 2026-06-23 | pending |
| r166 | e086 | 20000 | capital | cog | 2026-09-07 | pending |
| r167 | e135 | 45000 | hardware | bolt | 2026-07-10 | pending |
| r168 | e271 | 8000 | services | edge | 2026-06-29 | pending |
| r169 | e184 | 45000 | software | bolt | 2026-07-13 | pending |
| r170 | e169 | 38000 | software | fern | 2026-08-24 | pending |
| r171 | e273 | 45000 | capital | edge | 2026-07-27 | pending |
| r172 | e259 | 45000 | hardware | dyne | 2026-08-26 | cancelled |
| r173 | e237 | 60000 | hardware | fern | 2026-07-24 | pending |
| r174 | e181 | 38000 | services | cog | 2026-07-07 | pending |
| r175 | e162 | 45000 | software | acme | 2026-07-08 | pending |
| r176 | e260 | 3000 | services | bolt | 2026-09-01 | pending |
| r177 | e169 | 20000 | hardware | cog | 2026-08-04 | pending |
| r178 | e209 | 90000 | software | edge | 2026-09-14 | pending |
| r179 | e084 | 20000 | services | fern | 2026-07-26 | pending |
| r180 | e035 | 12000 | services | acme | 2026-09-13 | pending |
| r181 | e163 | 60000 | hardware | fern | 2026-07-16 | pending |
| r182 | e155 | 90000 | capital | bolt | 2026-06-04 | pending |
| r183 | e026 | 60000 | hardware | edge | 2026-09-15 | pending |
| r184 | e094 | 30000 | software | dyne | 2026-09-04 | pending |
| r185 | e127 | 45000 | software | dyne | 2026-09-03 | pending |
| r186 | e196 | 3000 | hardware | acme | 2026-09-07 | pending |
| r187 | e271 | 45000 | services | bolt | 2026-08-31 | pending |
| r188 | e147 | 45000 | services | fern | 2026-06-10 | cancelled |
| r189 | e132 | 90000 | hardware | dyne | 2026-07-09 | pending |
| r190 | e248 | 90000 | capital | edge | 2026-08-04 | pending |
| r191 | e014 | 38000 | software | cog | 2026-06-25 | pending |
| r192 | e119 | 90000 | capital | fern | 2026-06-06 | pending |
| r193 | e084 | 3000 | capital | dyne | 2026-06-27 | pending |
| r194 | e263 | 12000 | hardware | cog | 2026-08-14 | pending |
| r195 | e072 | 120000 | hardware | bolt | 2026-07-23 | pending |
| r196 | e250 | 45000 | software | edge | 2026-08-27 | pending |
| r197 | e250 | 30000 | capital | fern | 2026-07-19 | pending |
| r198 | e209 | 60000 | capital | dyne | 2026-08-18 | pending |
| r199 | e085 | 8000 | software | edge | 2026-08-15 | pending |
| r200 | e239 | 90000 | hardware | dyne | 2026-08-05 | pending |
| r201 | e223 | 38000 | hardware | dyne | 2026-08-20 | pending |
| r202 | e044 | 30000 | software | dyne | 2026-06-21 | pending |
| r203 | e109 | 3000 | software | dyne | 2026-06-10 | pending |
| r204 | e248 | 90000 | software | bolt | 2026-08-11 | pending |
| r205 | e075 | 12000 | capital | bolt | 2026-06-22 | pending |
| r206 | e252 | 38000 | capital | dyne | 2026-08-04 | pending |
| r207 | e109 | 60000 | services | acme | 2026-08-28 | pending |
| r208 | e126 | 20000 | capital | fern | 2026-06-18 | pending |
| r209 | e028 | 90000 | software | edge | 2026-08-12 | pending |
| r210 | e229 | 45000 | software | dyne | 2026-06-18 | pending |
| r211 | e148 | 3000 | services | fern | 2026-07-04 | pending |
| r212 | e273 | 45000 | services | cog | 2026-08-05 | pending |
| r213 | e009 | 12000 | services | edge | 2026-08-18 | pending |
| r214 | e001 | 45000 | capital | edge | 2026-06-16 | pending |
| r215 | e276 | 60000 | capital | cog | 2026-07-12 | pending |
| r216 | e019 | 12000 | hardware | acme | 2026-08-22 | pending |
| r217 | e271 | 8000 | capital | dyne | 2026-07-22 | pending |
| r218 | e057 | 30000 | software | acme | 2026-08-28 | pending |
| r219 | e273 | 8000 | services | bolt | 2026-09-11 | pending |
| r220 | e190 | 60000 | software | edge | 2026-06-05 | pending |
| r221 | e187 | 90000 | capital | fern | 2026-06-14 | pending |
| r222 | e217 | 60000 | services | acme | 2026-07-18 | pending |
| r223 | e255 | 30000 | services | edge | 2026-08-07 | pending |
| r224 | e137 | 3000 | services | bolt | 2026-08-11 | pending |
| r225 | e281 | 90000 | software | dyne | 2026-06-27 | pending |
| r226 | e223 | 3000 | services | edge | 2026-08-09 | pending |
| r227 | e006 | 8000 | capital | cog | 2026-07-14 | pending |
| r228 | e166 | 12000 | capital | bolt | 2026-06-10 | cancelled |
| r229 | e168 | 12000 | hardware | fern | 2026-06-11 | pending |
| r230 | e069 | 3000 | services | fern | 2026-06-03 | pending |
| r231 | e117 | 3000 | software | dyne | 2026-07-07 | pending |
| r232 | e186 | 60000 | hardware | dyne | 2026-09-09 | cancelled |

## emergency

A request flagged as an emergency.
Identified by: req. References: `req` refers to `req`.

| req |
|---|
| r002 |
| r007 |
| r016 |
| r024 |
| r025 |
| r026 |
| r034 |
| r048 |
| r051 |
| r054 |
| r058 |
| r065 |
| r078 |
| r093 |
| r096 |
| r100 |
| r110 |
| r112 |
| r126 |
| r130 |
| r132 |
| r142 |
| r148 |
| r151 |
| r152 |
| r155 |
| r157 |
| r167 |
| r168 |
| r176 |
| r182 |
| r183 |
| r184 |
| r185 |
| r188 |
| r201 |
| r204 |
| r208 |
| r209 |
| r212 |
| r216 |
| r219 |
| r221 |
| r227 |
| r230 |
| r231 |

## violation

An employee with a recorded policy violation.
Identified by: emp. References: `emp` refers to `emp`.

| emp |
|---|
| e015 |
| e033 |
| e035 |
| e042 |
| e054 |
| e065 |
| e070 |
| e073 |
| e078 |
| e109 |
| e118 |
| e157 |
| e169 |
| e177 |
| e180 |
| e187 |
| e188 |
| e191 |
| e201 |
| e212 |
| e218 |
| e220 |
| e225 |
| e227 |
| e250 |
| e253 |
| e279 |
| e280 |

## booked

Spend booked directly on a cost centre this quarter. A cost centre with no row has booked nothing.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| cc1_1_1_1 | 78000 |
| cc1_1_1_2 | 72000 |
| cc1_1_1_3 | 114000 |
| cc1_1_2_1 | 121000 |
| cc1_1_2_2 | 63000 |
| cc1_1_2_3 | 80000 |
| cc1_1_3_1 | 132000 |
| cc1_1_3_2 | 95000 |
| cc1_1_3_3 | 77000 |
| cc1_2_1_1 | 66000 |
| cc1_2_1_2 | 57000 |
| cc1_2_1_3 | 83000 |
| cc1_2_2_1 | 50000 |
| cc1_2_2_2 | 84000 |
| cc1_2_2_3 | 92000 |
| cc1_2_3_1 | 54000 |
| cc1_2_3_2 | 114000 |
| cc1_2_3_3 | 47000 |
| cc1_3_1_1 | 42000 |
| cc1_3_1_2 | 54000 |
| cc1_3_1_3 | 62000 |
| cc1_3_2_1 | 98000 |
| cc1_3_2_2 | 47000 |
| cc1_3_2_3 | 54000 |
| cc1_3_3_1 | 41000 |
| cc1_3_3_2 | 136000 |
| cc1_3_3_3 | 102000 |
| cc2_1_1_1 | 128000 |
| cc2_1_1_2 | 124000 |
| cc2_1_1_3 | 94000 |
| cc2_1_2_1 | 109000 |
| cc2_1_2_2 | 106000 |
| cc2_1_2_3 | 46000 |
| cc2_1_3_1 | 129000 |
| cc2_1_3_2 | 70000 |
| cc2_1_3_3 | 124000 |
| cc2_2_1_1 | 110000 |
| cc2_2_1_2 | 63000 |
| cc2_2_1_3 | 88000 |
| cc2_2_2_1 | 42000 |
| cc2_2_2_2 | 40000 |
| cc2_2_2_3 | 78000 |
| cc2_2_3_1 | 40000 |
| cc2_2_3_2 | 62000 |
| cc2_2_3_3 | 49000 |
| cc2_3_1_1 | 75000 |
| cc2_3_1_2 | 76000 |
| cc2_3_1_3 | 66000 |
| cc2_3_2_1 | 64000 |
| cc2_3_2_2 | 51000 |
| cc2_3_2_3 | 90000 |
| cc2_3_3_1 | 106000 |
| cc2_3_3_2 | 126000 |
| cc2_3_3_3 | 75000 |
| cc3_1_1_1 | 66000 |
| cc3_1_1_2 | 93000 |
| cc3_1_1_3 | 58000 |
| cc3_1_2_1 | 67000 |
| cc3_1_2_2 | 46000 |
| cc3_1_2_3 | 126000 |
| cc3_1_3_1 | 81000 |
| cc3_1_3_2 | 65000 |
| cc3_1_3_3 | 77000 |
| cc3_2_1_1 | 105000 |
| cc3_2_1_2 | 105000 |
| cc3_2_1_3 | 63000 |
| cc3_2_2_1 | 134000 |
| cc3_2_2_2 | 118000 |
| cc3_2_2_3 | 44000 |
| cc3_2_3_1 | 120000 |
| cc3_2_3_2 | 71000 |
| cc3_2_3_3 | 109000 |
| cc3_3_1_1 | 111000 |
| cc3_3_1_2 | 70000 |
| cc3_3_1_3 | 101000 |
| cc3_3_2_1 | 41000 |
| cc3_3_2_2 | 139000 |
| cc3_3_2_3 | 113000 |
| cc3_3_3_1 | 60000 |
| cc3_3_3_2 | 83000 |
| cc3_3_3_3 | 110000 |
| cc2 | 10000 |
| cc2_1_2 | 35000 |
| cc2_3_2 | 16000 |
| cc3_2 | 36000 |
| cc3_3 | 31000 |
| cc3_3_1 | 17000 |

## cap

The spending cap of a cost centre this quarter.
Identified by: cc. References: `cc` refers to `cc`.

| cc | amount |
|---|---|
| company | 8240000 |
| cc1 | 2220000 |
| cc1_1 | 1081000 |
| cc1_1_1 | 277000 |
| cc1_1_1_1 | 75000 |
| cc1_1_1_2 | 115000 |
| cc1_1_1_3 | 136000 |
| cc1_1_2 | 343000 |
| cc1_1_2_1 | 133000 |
| cc1_1_2_2 | 61000 |
| cc1_1_2_3 | 112000 |
| cc1_1_3 | 319000 |
| cc1_1_3_1 | 211000 |
| cc1_1_3_2 | 97000 |
| cc1_1_3_3 | 92000 |
| cc1_2 | 679000 |
| cc1_2_1 | 267000 |
| cc1_2_1_1 | 64000 |
| cc1_2_1_2 | 55000 |
| cc1_2_1_3 | 80000 |
| cc1_2_2 | 259000 |
| cc1_2_2_1 | 80000 |
| cc1_2_2_2 | 134000 |
| cc1_2_2_3 | 128000 |
| cc1_2_3 | 247000 |
| cc1_2_3_1 | 52000 |
| cc1_2_3_2 | 125000 |
| cc1_2_3_3 | 45000 |
| cc1_3 | 731000 |
| cc1_3_1 | 205000 |
| cc1_3_1_1 | 40000 |
| cc1_3_1_2 | 64000 |
| cc1_3_1_3 | 68000 |
| cc1_3_2 | 208000 |
| cc1_3_2_1 | 137000 |
| cc1_3_2_2 | 75000 |
| cc1_3_2_3 | 52000 |
| cc1_3_3 | 418000 |
| cc1_3_3_1 | 39000 |
| cc1_3_3_2 | 217000 |
| cc1_3_3_3 | 163000 |
| cc2 | 3438000 |
| cc2_1 | 1447000 |
| cc2_1_1 | 449000 |
| cc2_1_1_1 | 179000 |
| cc2_1_1_2 | 148000 |
| cc2_1_1_3 | 91000 |
| cc2_1_2 | 444000 |
| cc2_1_2_1 | 105000 |
| cc2_1_2_2 | 148000 |
| cc2_1_2_3 | 64000 |
| cc2_1_3 | 419000 |
| cc2_1_3_1 | 141000 |
| cc2_1_3_2 | 67000 |
| cc2_1_3_3 | 173000 |
| cc2_2 | 600000 |
| cc2_2_1 | 391000 |
| cc2_2_1_1 | 106000 |
| cc2_2_1_2 | 88000 |
| cc2_2_1_3 | 123000 |
| cc2_2_2 | 184000 |
| cc2_2_2_1 | 50000 |
| cc2_2_2_2 | 44000 |
| cc2_2_2_3 | 75000 |
| cc2_2_3 | 158000 |
| cc2_2_3_1 | 56000 |
| cc2_2_3_2 | 99000 |
| cc2_2_3_3 | 47000 |
| cc2_3 | 782000 |
| cc2_3_1 | 249000 |
| cc2_3_1_1 | 72000 |
| cc2_3_1_2 | 73000 |
| cc2_3_1_3 | 92000 |
| cc2_3_2 | 254000 |
| cc2_3_2_1 | 89000 |
| cc2_3_2_2 | 71000 |
| cc2_3_2_3 | 92000 |
| cc2_3_3 | 399000 |
| cc2_3_3_1 | 102000 |
| cc2_3_3_2 | 151000 |
| cc2_3_3_3 | 90000 |
| cc3 | 3198000 |
| cc3_1 | 712000 |
| cc3_1_1 | 282000 |
| cc3_1_1_1 | 64000 |
| cc3_1_1_2 | 90000 |
| cc3_1_1_3 | 92000 |
| cc3_1_2 | 358000 |
| cc3_1_2_1 | 107000 |
| cc3_1_2_2 | 47000 |
| cc3_1_2_3 | 201000 |
| cc3_1_3 | 234000 |
| cc3_1_3_1 | 97000 |
| cc3_1_3_2 | 104000 |
| cc3_1_3_3 | 84000 |
| cc3_2 | 1357000 |
| cc3_2_1 | 354000 |
| cc3_2_1_1 | 101000 |
| cc3_2_1_2 | 108000 |
| cc3_2_1_3 | 88000 |
| cc3_2_2 | 340000 |
| cc3_2_2_1 | 129000 |
| cc3_2_2_2 | 129000 |
| cc3_2_2_3 | 48000 |
| cc3_2_3 | 450000 |
| cc3_2_3_1 | 116000 |
| cc3_2_3_2 | 85000 |
| cc3_2_3_3 | 152000 |
| cc3_3 | 1314000 |
| cc3_3_1 | 388000 |
| cc3_3_1_1 | 114000 |
| cc3_3_1_2 | 72000 |
| cc3_3_1_3 | 111000 |
| cc3_3_2 | 439000 |
| cc3_3_2_1 | 42000 |
| cc3_3_2_2 | 194000 |
| cc3_3_2_3 | 124000 |
| cc3_3_3 | 265000 |
| cc3_3_3_1 | 66000 |
| cc3_3_3_2 | 116000 |
| cc3_3_3_3 | 176000 |

## today

The date on which the material was compiled.
Identified by: date.

| date |
|---|
| 2026-09-15 |

## role_limit_version

A dated version of a role's approval limit, valid from and to the given dates inclusive.
Identified by: role, valid_from.

| role | limit | valid_from | valid_to |
|---|---|---|---|
| analyst | 5000 | 2026-01-01 | 2026-12-31 |
| manager | 25000 | 2026-01-01 | 2026-07-31 |
| manager | 40000 | 2026-08-01 | 2026-12-31 |
| senior_manager | 50000 | 2026-01-01 | 2026-12-31 |
| director | 100000 | 2026-01-01 | 2026-12-31 |
| vp | 500000 | 2026-01-01 | 2026-12-31 |

## vendor_status

A vendor's status during a period, from and to the given dates inclusive.
Identified by: vendor, valid_from. References: `vendor` refers to `vendor`.

| vendor | status | valid_from | valid_to |
|---|---|---|---|
| acme | approved | 2026-01-01 | 2026-12-31 |
| bolt | approved | 2026-01-01 | 2026-07-31 |
| bolt | suspended | 2026-08-01 | 2026-12-31 |
| cog | approved | 2026-01-01 | 2026-12-31 |
| dyne | suspended | 2026-01-01 | 2026-06-30 |
| dyne | approved | 2026-07-01 | 2026-12-31 |
| edge | approved | 2026-01-01 | 2026-12-31 |
| fern | suspended | 2026-01-01 | 2026-12-31 |

## assignment

A source's record (hr or finance) that an employee belongs to a cost centre from the effective date on.
Identified by: emp, source, effective. References: `emp` refers to `emp`; `cc` refers to `cc`.

| emp | cc | source | effective |
|---|---|---|---|
| e000 | company | finance | 2026-01-01 |
| e000 | company | hr | 2026-01-01 |
| e001 | cc1 | finance | 2026-01-01 |
| e001 | cc1 | hr | 2026-01-01 |
| e002 | cc1_1 | finance | 2026-01-01 |
| e002 | cc1_1 | hr | 2026-01-01 |
| e003 | cc1_1_1 | finance | 2026-01-01 |
| e003 | cc1_1_1 | hr | 2026-01-01 |
| e004 | cc1_1_1_1 | finance | 2026-01-01 |
| e004 | cc1_1_1_1 | hr | 2026-01-01 |
| e005 | cc1_1_1_2 | finance | 2026-01-01 |
| e005 | cc1_1_1_2 | hr | 2026-01-01 |
| e006 | cc1_1_1_3 | finance | 2026-01-01 |
| e006 | cc1_1_1_3 | hr | 2026-01-01 |
| e007 | cc1_1_2 | finance | 2026-01-01 |
| e007 | cc1_1_2 | hr | 2026-01-01 |
| e008 | cc1_1_2_1 | finance | 2026-01-01 |
| e008 | cc1_1_2_1 | hr | 2026-01-01 |
| e009 | cc1_1_2_2 | finance | 2026-01-01 |
| e009 | cc1_1_2_2 | hr | 2026-01-01 |
| e010 | cc1_1_2_3 | finance | 2026-01-01 |
| e010 | cc1_1_2_3 | hr | 2026-01-01 |
| e011 | cc1_1_3 | finance | 2026-01-01 |
| e011 | cc1_1_3 | hr | 2026-01-01 |
| e012 | cc1_1_3_1 | finance | 2026-01-01 |
| e012 | cc1_1_3_1 | hr | 2026-01-01 |
| e013 | cc1_1_3_2 | finance | 2026-01-01 |
| e013 | cc1_1_3_2 | hr | 2026-01-01 |
| e014 | cc1_1_3_3 | finance | 2026-01-01 |
| e014 | cc1_1_3_3 | hr | 2026-01-01 |
| e015 | cc1_2 | finance | 2026-01-01 |
| e015 | cc1_2 | hr | 2026-01-01 |
| e016 | cc1_2_1 | finance | 2026-01-01 |
| e016 | cc1_2_1 | hr | 2026-01-01 |
| e017 | cc1_2_1_1 | finance | 2026-01-01 |
| e017 | cc1_2_1_1 | hr | 2026-01-01 |
| e018 | cc1_2_1_2 | finance | 2026-01-01 |
| e018 | cc1_2_1_2 | hr | 2026-01-01 |
| e019 | cc1_2_1_3 | finance | 2026-01-01 |
| e019 | cc1_2_1_3 | hr | 2026-01-01 |
| e020 | cc1_2_2 | finance | 2026-01-01 |
| e020 | cc1_2_2 | hr | 2026-01-01 |
| e021 | cc1_2_2_1 | finance | 2026-01-01 |
| e021 | cc1_2_2_1 | hr | 2026-01-01 |
| e022 | cc1_2_2_2 | finance | 2026-01-01 |
| e022 | cc1_2_2_2 | hr | 2026-01-01 |
| e023 | cc1_2_2_3 | finance | 2026-01-01 |
| e023 | cc1_2_2_3 | hr | 2026-01-01 |
| e024 | cc1_2_3 | finance | 2026-01-01 |
| e024 | cc1_2_3 | hr | 2026-01-01 |
| e025 | cc1_2_3_1 | finance | 2026-01-01 |
| e025 | cc1_2_3_1 | hr | 2026-01-01 |
| e026 | cc1_2_3_2 | finance | 2026-01-01 |
| e026 | cc1_2_3_2 | hr | 2026-01-01 |
| e027 | cc1_2_3_3 | finance | 2026-01-01 |
| e027 | cc1_2_3_3 | hr | 2026-01-01 |
| e028 | cc1_3 | finance | 2026-01-01 |
| e028 | cc1_3 | hr | 2026-01-01 |
| e029 | cc1_3_1 | finance | 2026-01-01 |
| e029 | cc1_3_1 | hr | 2026-01-01 |
| e030 | cc1_3_1_1 | finance | 2026-01-01 |
| e030 | cc1_3_1_1 | hr | 2026-01-01 |
| e031 | cc1_3_1_2 | finance | 2026-01-01 |
| e031 | cc1_3_1_2 | hr | 2026-01-01 |
| e032 | cc1_3_1_3 | finance | 2026-01-01 |
| e032 | cc1_3_1_3 | hr | 2026-01-01 |
| e033 | cc1_3_2 | finance | 2026-01-01 |
| e033 | cc1_3_2 | hr | 2026-01-01 |
| e034 | cc1_3_2_1 | finance | 2026-01-01 |
| e034 | cc1_3_2_1 | hr | 2026-01-01 |
| e035 | cc1_3_2_2 | finance | 2026-01-01 |
| e035 | cc1_3_2_2 | hr | 2026-01-01 |
| e036 | cc1_3_2_3 | finance | 2026-01-01 |
| e036 | cc1_3_2_3 | hr | 2026-01-01 |
| e037 | cc1_3_3 | finance | 2026-01-01 |
| e037 | cc1_3_3 | hr | 2026-01-01 |
| e038 | cc1_3_3_1 | finance | 2026-01-01 |
| e038 | cc1_3_3_1 | hr | 2026-01-01 |
| e039 | cc1_3_3_2 | finance | 2026-01-01 |
| e039 | cc1_3_3_2 | hr | 2026-01-01 |
| e040 | cc1_3_3_3 | finance | 2026-01-01 |
| e040 | cc1_3_3_3 | hr | 2026-01-01 |
| e041 | cc2 | finance | 2026-01-01 |
| e041 | cc2 | hr | 2026-01-01 |
| e042 | cc2_1 | finance | 2026-01-01 |
| e042 | cc2_1 | hr | 2026-01-01 |
| e043 | cc2_1_1 | finance | 2026-01-01 |
| e043 | cc2_1_1 | hr | 2026-01-01 |
| e044 | cc2_1_1_1 | finance | 2026-01-01 |
| e044 | cc2_1_1_1 | hr | 2026-01-01 |
| e045 | cc2_1_1_2 | finance | 2026-01-01 |
| e045 | cc2_1_1_2 | hr | 2026-01-01 |
| e046 | cc2_1_1_3 | finance | 2026-01-01 |
| e046 | cc2_1_1_3 | hr | 2026-01-01 |
| e047 | cc2_1_2 | finance | 2026-01-01 |
| e047 | cc2_1_2 | hr | 2026-01-01 |
| e048 | cc2_1_2_1 | finance | 2026-01-01 |
| e048 | cc2_1_2_1 | hr | 2026-01-01 |
| e049 | cc2_1_2_2 | finance | 2026-01-01 |
| e049 | cc2_1_2_2 | hr | 2026-01-01 |
| e050 | cc2_1_2_3 | finance | 2026-01-01 |
| e050 | cc2_1_2_3 | hr | 2026-01-01 |
| e051 | cc2_1_3 | finance | 2026-01-01 |
| e051 | cc2_1_3 | hr | 2026-01-01 |
| e052 | cc2_1_3_1 | finance | 2026-01-01 |
| e052 | cc2_1_3_1 | hr | 2026-01-01 |
| e053 | cc2_1_3_2 | finance | 2026-01-01 |
| e053 | cc2_1_3_2 | hr | 2026-01-01 |
| e054 | cc2_1_3_3 | finance | 2026-01-01 |
| e054 | cc2_1_3_3 | hr | 2026-01-01 |
| e055 | cc2_2 | finance | 2026-01-01 |
| e055 | cc2_2 | hr | 2026-01-01 |
| e056 | cc2_2_1 | finance | 2026-01-01 |
| e056 | cc2_2_1 | hr | 2026-01-01 |
| e057 | cc2_2_1_1 | finance | 2026-01-01 |
| e057 | cc2_2_1_1 | hr | 2026-01-01 |
| e058 | cc2_2_1_2 | finance | 2026-01-01 |
| e058 | cc2_2_1_2 | hr | 2026-01-01 |
| e059 | cc2_2_1_3 | finance | 2026-01-01 |
| e059 | cc2_2_1_3 | hr | 2026-01-01 |
| e060 | cc2_2_2 | finance | 2026-01-01 |
| e060 | cc2_2_2 | hr | 2026-01-01 |
| e061 | cc2_2_2_1 | finance | 2026-01-01 |
| e061 | cc2_2_2_1 | hr | 2026-01-01 |
| e062 | cc2_2_2_2 | finance | 2026-01-01 |
| e062 | cc2_2_2_2 | hr | 2026-01-01 |
| e063 | cc2_2_2_3 | finance | 2026-01-01 |
| e063 | cc2_2_2_3 | hr | 2026-01-01 |
| e064 | cc2_2_3 | finance | 2026-01-01 |
| e064 | cc2_2_3 | hr | 2026-01-01 |
| e065 | cc2_2_3_1 | finance | 2026-01-01 |
| e065 | cc2_2_3_1 | hr | 2026-01-01 |
| e066 | cc2_2_3_2 | finance | 2026-01-01 |
| e066 | cc2_2_3_2 | hr | 2026-01-01 |
| e067 | cc2_2_3_3 | finance | 2026-01-01 |
| e067 | cc2_2_3_3 | hr | 2026-01-01 |
| e068 | cc2_3 | finance | 2026-01-01 |
| e068 | cc2_3 | hr | 2026-01-01 |
| e069 | cc2_3_1 | finance | 2026-01-01 |
| e069 | cc2_3_1 | hr | 2026-01-01 |
| e070 | cc2_3_1_1 | finance | 2026-01-01 |
| e070 | cc2_3_1_1 | hr | 2026-01-01 |
| e071 | cc2_3_1_2 | finance | 2026-01-01 |
| e071 | cc2_3_1_2 | hr | 2026-01-01 |
| e072 | cc2_3_1_3 | finance | 2026-01-01 |
| e072 | cc2_3_1_3 | hr | 2026-01-01 |
| e073 | cc2_3_2 | finance | 2026-01-01 |
| e073 | cc2_3_2 | hr | 2026-01-01 |
| e074 | cc2_3_2_1 | finance | 2026-01-01 |
| e074 | cc2_3_2_1 | hr | 2026-01-01 |
| e075 | cc2_3_2_2 | finance | 2026-01-01 |
| e075 | cc2_3_2_2 | hr | 2026-01-01 |
| e076 | cc2_3_2_3 | finance | 2026-01-01 |
| e076 | cc2_3_2_3 | hr | 2026-01-01 |
| e077 | cc2_3_3 | finance | 2026-01-01 |
| e077 | cc2_3_3 | hr | 2026-01-01 |
| e078 | cc2_3_3_1 | finance | 2026-01-01 |
| e078 | cc2_3_3_1 | hr | 2026-01-01 |
| e079 | cc2_3_3_2 | finance | 2026-01-01 |
| e079 | cc2_3_3_2 | hr | 2026-01-01 |
| e080 | cc2_3_3_3 | finance | 2026-01-01 |
| e080 | cc2_3_3_3 | hr | 2026-01-01 |
| e081 | cc3 | finance | 2026-01-01 |
| e081 | cc3 | hr | 2026-01-01 |
| e082 | cc3_1 | finance | 2026-01-01 |
| e082 | cc3_1 | hr | 2026-01-01 |
| e083 | cc3_1_1 | finance | 2026-01-01 |
| e083 | cc3_1_1 | hr | 2026-01-01 |
| e084 | cc3_1_1_1 | finance | 2026-01-01 |
| e084 | cc3_1_1_1 | hr | 2026-01-01 |
| e085 | cc3_1_1_2 | finance | 2026-01-01 |
| e085 | cc3_1_1_2 | hr | 2026-01-01 |
| e086 | cc3_1_1_3 | finance | 2026-01-01 |
| e086 | cc3_1_1_3 | hr | 2026-01-01 |
| e087 | cc3_1_2 | finance | 2026-01-01 |
| e087 | cc3_1_2 | hr | 2026-01-01 |
| e088 | cc3_1_2_1 | finance | 2026-01-01 |
| e088 | cc3_1_2_1 | hr | 2026-01-01 |
| e089 | cc3_1_2_2 | finance | 2026-01-01 |
| e089 | cc3_1_2_2 | hr | 2026-01-01 |
| e090 | cc3_1_2_3 | finance | 2026-01-01 |
| e090 | cc3_1_2_3 | hr | 2026-01-01 |
| e091 | cc3_1_3 | finance | 2026-01-01 |
| e091 | cc3_1_3 | hr | 2026-01-01 |
| e092 | cc3_1_3_1 | finance | 2026-01-01 |
| e092 | cc3_1_3_1 | hr | 2026-01-01 |
| e093 | cc3_1_3_2 | finance | 2026-01-01 |
| e093 | cc3_1_3_2 | hr | 2026-01-01 |
| e094 | cc3_1_3_3 | finance | 2026-01-01 |
| e094 | cc3_1_3_3 | hr | 2026-01-01 |
| e095 | cc3_2 | finance | 2026-01-01 |
| e095 | cc3_2 | hr | 2026-01-01 |
| e096 | cc3_2_1 | finance | 2026-01-01 |
| e096 | cc3_2_1 | hr | 2026-01-01 |
| e097 | cc3_2_1_1 | finance | 2026-01-01 |
| e097 | cc3_2_1_1 | hr | 2026-01-01 |
| e098 | cc3_2_1_2 | finance | 2026-01-01 |
| e098 | cc3_2_1_2 | hr | 2026-01-01 |
| e099 | cc3_2_1_3 | finance | 2026-01-01 |
| e099 | cc3_2_1_3 | hr | 2026-01-01 |
| e100 | cc3_2_2 | finance | 2026-01-01 |
| e100 | cc3_2_2 | hr | 2026-01-01 |
| e101 | cc3_2_2_1 | finance | 2026-01-01 |
| e101 | cc3_2_2_1 | hr | 2026-01-01 |
| e102 | cc3_2_2_2 | finance | 2026-01-01 |
| e102 | cc3_2_2_2 | hr | 2026-01-01 |
| e103 | cc3_2_2_3 | finance | 2026-01-01 |
| e103 | cc3_2_2_3 | hr | 2026-01-01 |
| e104 | cc3_2_3 | finance | 2026-01-01 |
| e104 | cc3_2_3 | hr | 2026-01-01 |
| e105 | cc3_2_3_1 | finance | 2026-01-01 |
| e105 | cc3_2_3_1 | hr | 2026-01-01 |
| e106 | cc3_2_3_2 | finance | 2026-01-01 |
| e106 | cc3_2_3_2 | hr | 2026-01-01 |
| e107 | cc3_2_3_3 | finance | 2026-01-01 |
| e107 | cc3_2_3_3 | hr | 2026-01-01 |
| e108 | cc3_3 | finance | 2026-01-01 |
| e108 | cc3_3 | hr | 2026-01-01 |
| e109 | cc3_3_1 | finance | 2026-01-01 |
| e109 | cc3_3_1 | hr | 2026-01-01 |
| e110 | cc3_3_1_1 | finance | 2026-01-01 |
| e110 | cc3_3_1_1 | hr | 2026-01-01 |
| e111 | cc3_3_1_2 | finance | 2026-01-01 |
| e111 | cc3_3_1_2 | hr | 2026-01-01 |
| e112 | cc3_3_1_3 | finance | 2026-01-01 |
| e112 | cc3_3_1_3 | hr | 2026-01-01 |
| e113 | cc3_3_2 | finance | 2026-01-01 |
| e113 | cc3_3_2 | hr | 2026-01-01 |
| e114 | cc3_3_2_1 | finance | 2026-01-01 |
| e114 | cc3_3_2_1 | hr | 2026-01-01 |
| e115 | cc3_3_2_2 | finance | 2026-01-01 |
| e115 | cc3_3_2_2 | hr | 2026-01-01 |
| e116 | cc3_3_2_3 | finance | 2026-01-01 |
| e116 | cc3_3_2_3 | hr | 2026-01-01 |
| e117 | cc3_3_3 | finance | 2026-01-01 |
| e117 | cc3_3_3 | hr | 2026-01-01 |
| e118 | cc3_3_3_1 | finance | 2026-01-01 |
| e118 | cc3_3_3_1 | hr | 2026-01-01 |
| e119 | cc3_3_3_2 | finance | 2026-01-01 |
| e119 | cc3_3_3_2 | hr | 2026-01-01 |
| e120 | cc3_3_3_3 | finance | 2026-01-01 |
| e120 | cc3_3_3_3 | hr | 2026-01-01 |
| e121 | cc1_1_1_1 | finance | 2026-01-01 |
| e121 | cc1_1_1_1 | hr | 2026-01-01 |
| e122 | cc1_1_1_1 | finance | 2026-01-01 |
| e122 | cc1_1_1_1 | hr | 2026-01-01 |
| e123 | cc1_1_1_2 | finance | 2026-01-01 |
| e123 | cc1_1_1_2 | hr | 2026-01-01 |
| e124 | cc1_1_1_2 | finance | 2026-01-01 |
| e124 | cc1_1_1_2 | hr | 2026-01-01 |
| e125 | cc1_1_1_3 | finance | 2026-01-01 |
| e125 | cc1_1_1_3 | hr | 2026-01-01 |
| e126 | cc1_1_1_3 | finance | 2026-01-01 |
| e126 | cc3_3_3_3 | finance | 2026-08-08 |
| e126 | cc1_1_1_3 | hr | 2026-01-01 |
| e126 | cc3_3_3_3 | hr | 2026-07-02 |
| e127 | cc1_1_2_1 | finance | 2026-01-01 |
| e127 | cc1_1_2_1 | hr | 2026-01-01 |
| e128 | cc1_1_2_1 | finance | 2026-01-01 |
| e128 | cc1_1_2_1 | hr | 2026-01-01 |
| e129 | cc1_1_2_2 | finance | 2026-01-01 |
| e129 | cc1_1_2_2 | hr | 2026-01-01 |
| e130 | cc1_1_2_2 | finance | 2026-01-01 |
| e130 | cc1_1_2_2 | hr | 2026-01-01 |
| e131 | cc1_1_2_3 | finance | 2026-01-01 |
| e131 | cc1_1_2_3 | hr | 2026-01-01 |
| e132 | cc1_1_2_3 | finance | 2026-01-01 |
| e132 | cc1_1_2_3 | hr | 2026-01-01 |
| e133 | cc1_1_3_1 | finance | 2026-01-01 |
| e133 | cc1_1_3_1 | hr | 2026-01-01 |
| e134 | cc1_1_3_1 | finance | 2026-01-01 |
| e134 | cc1_1_3_1 | hr | 2026-01-01 |
| e135 | cc1_1_3_2 | finance | 2026-01-01 |
| e135 | cc1_1_3_2 | hr | 2026-01-01 |
| e136 | cc1_1_3_2 | finance | 2026-01-01 |
| e136 | cc1_1_3_2 | hr | 2026-01-01 |
| e137 | cc1_1_3_3 | finance | 2026-01-01 |
| e137 | cc1_1_3_3 | hr | 2026-01-01 |
| e138 | cc1_1_3_3 | finance | 2026-01-01 |
| e138 | cc1_1_3_3 | hr | 2026-01-01 |
| e139 | cc1_2_1_1 | finance | 2026-01-01 |
| e139 | cc1_2_1_1 | hr | 2026-01-01 |
| e140 | cc1_2_1_1 | finance | 2026-01-01 |
| e140 | cc1_2_1_1 | hr | 2026-01-01 |
| e141 | cc1_2_1_2 | finance | 2026-01-01 |
| e141 | cc1_2_1_2 | hr | 2026-01-01 |
| e142 | cc1_2_1_2 | finance | 2026-01-01 |
| e142 | cc1_2_1_2 | hr | 2026-01-01 |
| e143 | cc1_2_1_3 | finance | 2026-01-01 |
| e143 | cc1_2_1_3 | hr | 2026-01-01 |
| e144 | cc1_2_1_3 | finance | 2026-01-01 |
| e144 | cc1_2_1_3 | hr | 2026-01-01 |
| e145 | cc1_2_2_1 | finance | 2026-01-01 |
| e145 | cc1_2_2_1 | hr | 2026-01-01 |
| e146 | cc1_2_2_1 | finance | 2026-01-01 |
| e146 | cc1_2_2_1 | hr | 2026-01-01 |
| e147 | cc1_2_2_2 | finance | 2026-01-01 |
| e147 | cc1_2_2_2 | hr | 2026-01-01 |
| e148 | cc1_2_2_2 | finance | 2026-01-01 |
| e148 | cc1_2_2_2 | hr | 2026-01-01 |
| e149 | cc1_2_2_3 | finance | 2026-01-01 |
| e149 | cc1_2_2_3 | hr | 2026-01-01 |
| e150 | cc1_2_2_3 | finance | 2026-01-01 |
| e150 | cc1_2_2_3 | hr | 2026-01-01 |
| e151 | cc1_2_3_1 | finance | 2026-01-01 |
| e151 | cc1_2_3_1 | hr | 2026-01-01 |
| e152 | cc1_2_3_1 | finance | 2026-01-01 |
| e152 | cc1_2_3_1 | hr | 2026-01-01 |
| e153 | cc1_2_3_2 | finance | 2026-01-01 |
| e153 | cc1_2_3_2 | hr | 2026-01-01 |
| e154 | cc1_2_3_2 | finance | 2026-01-01 |
| e154 | cc1_2_3_2 | hr | 2026-01-01 |
| e155 | cc1_2_3_3 | finance | 2026-01-01 |
| e155 | cc1_2_3_3 | hr | 2026-01-01 |
| e155 | cc1_1_3_1 | hr | 2026-08-25 |
| e156 | cc1_2_3_3 | finance | 2026-01-01 |
| e156 | cc1_2_3_3 | hr | 2026-01-01 |
| e156 | cc2_1_2_1 | hr | 2026-08-09 |
| e157 | cc1_3_1_1 | finance | 2026-01-01 |
| e157 | cc1_3_1_1 | hr | 2026-01-01 |
| e158 | cc1_3_1_1 | finance | 2026-01-01 |
| e158 | cc1_3_1_1 | hr | 2026-01-01 |
| e159 | cc1_3_1_2 | finance | 2026-01-01 |
| e159 | cc1_3_1_2 | hr | 2026-01-01 |
| e160 | cc1_3_1_2 | finance | 2026-01-01 |
| e160 | cc1_3_1_2 | hr | 2026-01-01 |
| e161 | cc1_3_1_3 | finance | 2026-01-01 |
| e161 | cc1_3_1_3 | hr | 2026-01-01 |
| e162 | cc1_3_1_3 | finance | 2026-01-01 |
| e162 | cc1_3_1_3 | hr | 2026-01-01 |
| e163 | cc1_3_2_1 | finance | 2026-01-01 |
| e163 | cc1_3_2_1 | hr | 2026-01-01 |
| e164 | cc1_3_2_1 | finance | 2026-01-01 |
| e164 | cc1_3_2_1 | hr | 2026-01-01 |
| e165 | cc1_3_2_2 | finance | 2026-01-01 |
| e165 | cc1_3_2_2 | hr | 2026-01-01 |
| e166 | cc1_3_2_2 | finance | 2026-01-01 |
| e166 | cc1_3_2_2 | hr | 2026-01-01 |
| e167 | cc1_3_2_3 | finance | 2026-01-01 |
| e167 | cc1_3_2_3 | hr | 2026-01-01 |
| e168 | cc1_3_2_3 | finance | 2026-01-01 |
| e168 | cc1_3_2_3 | hr | 2026-01-01 |
| e169 | cc1_3_3_1 | finance | 2026-01-01 |
| e169 | cc1_3_3_1 | hr | 2026-01-01 |
| e170 | cc1_3_3_1 | finance | 2026-01-01 |
| e170 | cc1_3_3_1 | hr | 2026-01-01 |
| e171 | cc1_3_3_2 | finance | 2026-01-01 |
| e171 | cc1_3_3_2 | hr | 2026-01-01 |
| e172 | cc1_3_3_2 | finance | 2026-01-01 |
| e172 | cc1_3_3_2 | hr | 2026-01-01 |
| e173 | cc1_3_3_3 | finance | 2026-01-01 |
| e173 | cc3_2_1_2 | finance | 2026-07-01 |
| e173 | cc1_3_3_3 | hr | 2026-01-01 |
| e173 | cc3_2_1_2 | hr | 2026-06-17 |
| e174 | cc1_3_3_3 | finance | 2026-01-01 |
| e174 | cc1_3_3_3 | hr | 2026-01-01 |
| e175 | cc2_1_1_1 | finance | 2026-01-01 |
| e175 | cc2_1_1_1 | hr | 2026-01-01 |
| e176 | cc2_1_1_1 | finance | 2026-01-01 |
| e176 | cc2_1_1_1 | hr | 2026-01-01 |
| e177 | cc2_1_1_2 | finance | 2026-01-01 |
| e177 | cc2_1_1_2 | hr | 2026-01-01 |
| e178 | cc2_1_1_2 | finance | 2026-01-01 |
| e178 | cc2_1_1_2 | hr | 2026-01-01 |
| e179 | cc2_1_1_3 | finance | 2026-01-01 |
| e179 | cc2_1_1_3 | hr | 2026-01-01 |
| e180 | cc2_1_1_3 | finance | 2026-01-01 |
| e180 | cc2_1_1_3 | hr | 2026-01-01 |
| e181 | cc2_1_2_1 | finance | 2026-01-01 |
| e181 | cc2_1_2_1 | hr | 2026-01-01 |
| e182 | cc2_1_2_1 | finance | 2026-01-01 |
| e182 | cc2_1_2_1 | hr | 2026-01-01 |
| e183 | cc2_1_2_2 | finance | 2026-01-01 |
| e183 | cc2_1_2_2 | hr | 2026-01-01 |
| e184 | cc2_1_2_2 | finance | 2026-01-01 |
| e184 | cc2_1_2_2 | hr | 2026-01-01 |
| e185 | cc2_1_2_3 | finance | 2026-01-01 |
| e185 | cc2_1_2_3 | hr | 2026-01-01 |
| e186 | cc2_1_2_3 | finance | 2026-01-01 |
| e186 | cc2_1_2_3 | hr | 2026-01-01 |
| e187 | cc2_1_3_1 | finance | 2026-01-01 |
| e187 | cc2_1_3_1 | hr | 2026-01-01 |
| e188 | cc2_1_3_1 | finance | 2026-01-01 |
| e188 | cc2_1_3_1 | hr | 2026-01-01 |
| e189 | cc2_1_3_2 | finance | 2026-01-01 |
| e189 | cc2_1_3_2 | hr | 2026-01-01 |
| e190 | cc2_1_3_2 | finance | 2026-01-01 |
| e190 | cc2_1_3_2 | hr | 2026-01-01 |
| e191 | cc2_1_3_3 | finance | 2026-01-01 |
| e191 | cc2_1_3_3 | hr | 2026-01-01 |
| e192 | cc2_1_3_3 | finance | 2026-01-01 |
| e192 | cc2_1_3_3 | hr | 2026-01-01 |
| e193 | cc2_2_1_1 | finance | 2026-01-01 |
| e193 | cc3_2_3_2 | finance | 2026-09-02 |
| e193 | cc2_2_1_1 | hr | 2026-01-01 |
| e193 | cc3_2_3_2 | hr | 2026-07-27 |
| e194 | cc2_2_1_1 | finance | 2026-01-01 |
| e194 | cc2_2_1_1 | hr | 2026-01-01 |
| e195 | cc2_2_1_2 | finance | 2026-01-01 |
| e195 | cc2_2_1_2 | hr | 2026-01-01 |
| e196 | cc2_2_1_2 | finance | 2026-01-01 |
| e196 | cc2_2_1_2 | hr | 2026-01-01 |
| e197 | cc2_2_1_3 | finance | 2026-01-01 |
| e197 | cc2_2_1_3 | hr | 2026-01-01 |
| e198 | cc2_2_1_3 | finance | 2026-01-01 |
| e198 | cc1_3_2_2 | finance | 2026-07-14 |
| e198 | cc2_2_1_3 | hr | 2026-01-01 |
| e198 | cc1_3_2_2 | hr | 2026-06-28 |
| e199 | cc2_2_2_1 | finance | 2026-01-01 |
| e199 | cc2_2_2_1 | hr | 2026-01-01 |
| e200 | cc2_2_2_1 | finance | 2026-01-01 |
| e200 | cc2_2_2_1 | hr | 2026-01-01 |
| e201 | cc2_2_2_2 | finance | 2026-01-01 |
| e201 | cc2_2_2_2 | hr | 2026-01-01 |
| e202 | cc2_2_2_2 | finance | 2026-01-01 |
| e202 | cc2_2_2_2 | hr | 2026-01-01 |
| e203 | cc2_2_2_3 | finance | 2026-01-01 |
| e203 | cc2_2_2_3 | hr | 2026-01-01 |
| e204 | cc2_2_2_3 | finance | 2026-01-01 |
| e204 | cc2_2_2_3 | hr | 2026-01-01 |
| e205 | cc2_2_3_1 | finance | 2026-01-01 |
| e205 | cc2_2_3_1 | hr | 2026-01-01 |
| e206 | cc2_2_3_1 | finance | 2026-01-01 |
| e206 | cc2_2_3_1 | hr | 2026-01-01 |
| e207 | cc2_2_3_2 | finance | 2026-01-01 |
| e207 | cc2_2_3_2 | hr | 2026-01-01 |
| e208 | cc2_2_3_2 | finance | 2026-01-01 |
| e208 | cc2_2_3_2 | hr | 2026-01-01 |
| e209 | cc2_2_3_3 | finance | 2026-01-01 |
| e209 | cc2_2_3_3 | hr | 2026-01-01 |
| e210 | cc2_2_3_3 | finance | 2026-01-01 |
| e210 | cc2_2_3_3 | hr | 2026-01-01 |
| e211 | cc2_3_1_1 | finance | 2026-01-01 |
| e211 | cc2_3_1_1 | hr | 2026-01-01 |
| e212 | cc2_3_1_1 | finance | 2026-01-01 |
| e212 | cc2_3_1_1 | hr | 2026-01-01 |
| e213 | cc2_3_1_2 | finance | 2026-01-01 |
| e213 | cc2_1_3_1 | finance | 2026-09-03 |
| e213 | cc2_3_1_2 | hr | 2026-01-01 |
| e213 | cc2_1_3_1 | hr | 2026-08-18 |
| e214 | cc2_3_1_2 | finance | 2026-01-01 |
| e214 | cc2_3_1_2 | hr | 2026-01-01 |
| e215 | cc2_3_1_3 | finance | 2026-01-01 |
| e215 | cc2_3_1_3 | hr | 2026-01-01 |
| e216 | cc2_3_1_3 | finance | 2026-01-01 |
| e216 | cc2_3_1_3 | hr | 2026-01-01 |
| e217 | cc2_3_2_1 | finance | 2026-01-01 |
| e217 | cc2_3_2_1 | hr | 2026-01-01 |
| e218 | cc2_3_2_1 | finance | 2026-01-01 |
| e218 | cc2_3_2_1 | hr | 2026-01-01 |
| e219 | cc2_3_2_2 | finance | 2026-01-01 |
| e219 | cc2_3_2_2 | hr | 2026-01-01 |
| e220 | cc2_3_2_2 | finance | 2026-01-01 |
| e220 | cc2_3_2_2 | hr | 2026-01-01 |
| e221 | cc2_3_2_3 | finance | 2026-01-01 |
| e221 | cc2_3_2_3 | hr | 2026-01-01 |
| e222 | cc2_3_2_3 | finance | 2026-01-01 |
| e222 | cc2_3_2_3 | hr | 2026-01-01 |
| e223 | cc2_3_3_1 | finance | 2026-01-01 |
| e223 | cc2_3_3_1 | hr | 2026-01-01 |
| e224 | cc2_3_3_1 | finance | 2026-01-01 |
| e224 | cc2_3_3_1 | hr | 2026-01-01 |
| e225 | cc2_3_3_2 | finance | 2026-01-01 |
| e225 | cc2_3_3_2 | hr | 2026-01-01 |
| e226 | cc2_3_3_2 | finance | 2026-01-01 |
| e226 | cc2_3_3_2 | hr | 2026-01-01 |
| e227 | cc2_3_3_3 | finance | 2026-01-01 |
| e227 | cc2_3_3_3 | hr | 2026-01-01 |
| e228 | cc2_3_3_3 | finance | 2026-01-01 |
| e228 | cc2_3_3_3 | hr | 2026-01-01 |
| e229 | cc3_1_1_1 | finance | 2026-01-01 |
| e229 | cc2_3_2_3 | finance | 2026-09-03 |
| e229 | cc3_1_1_1 | hr | 2026-01-01 |
| e229 | cc2_3_2_3 | hr | 2026-08-01 |
| e230 | cc3_1_1_1 | finance | 2026-01-01 |
| e230 | cc3_1_1_1 | hr | 2026-01-01 |
| e231 | cc3_1_1_2 | finance | 2026-01-01 |
| e231 | cc3_1_1_2 | hr | 2026-01-01 |
| e232 | cc3_1_1_2 | finance | 2026-01-01 |
| e232 | cc3_1_1_2 | hr | 2026-01-01 |
| e233 | cc3_1_1_3 | finance | 2026-01-01 |
| e233 | cc3_1_1_3 | hr | 2026-01-01 |
| e234 | cc3_1_1_3 | finance | 2026-01-01 |
| e234 | cc3_1_1_3 | hr | 2026-01-01 |
| e235 | cc3_1_2_1 | finance | 2026-01-01 |
| e235 | cc3_1_2_1 | hr | 2026-01-01 |
| e236 | cc3_1_2_1 | finance | 2026-01-01 |
| e236 | cc3_1_2_1 | hr | 2026-01-01 |
| e237 | cc3_1_2_2 | finance | 2026-01-01 |
| e237 | cc3_1_2_2 | hr | 2026-01-01 |
| e238 | cc3_1_2_2 | finance | 2026-01-01 |
| e238 | cc3_1_2_2 | hr | 2026-01-01 |
| e239 | cc3_1_2_3 | finance | 2026-01-01 |
| e239 | cc3_1_2_3 | hr | 2026-01-01 |
| e240 | cc3_1_2_3 | finance | 2026-01-01 |
| e240 | cc3_1_2_3 | hr | 2026-01-01 |
| e241 | cc3_1_3_1 | finance | 2026-01-01 |
| e241 | cc3_1_3_1 | hr | 2026-01-01 |
| e242 | cc3_1_3_1 | finance | 2026-01-01 |
| e242 | cc3_1_3_1 | hr | 2026-01-01 |
| e243 | cc3_1_3_2 | finance | 2026-01-01 |
| e243 | cc3_1_3_2 | hr | 2026-01-01 |
| e244 | cc3_1_3_2 | finance | 2026-01-01 |
| e244 | cc3_1_3_2 | hr | 2026-01-01 |
| e245 | cc3_1_3_3 | finance | 2026-01-01 |
| e245 | cc3_1_3_3 | hr | 2026-01-01 |
| e246 | cc3_1_3_3 | finance | 2026-01-01 |
| e246 | cc3_1_3_3 | hr | 2026-01-01 |
| e247 | cc3_2_1_1 | finance | 2026-01-01 |
| e247 | cc3_2_1_1 | hr | 2026-01-01 |
| e248 | cc3_2_1_1 | finance | 2026-01-01 |
| e248 | cc3_2_1_1 | hr | 2026-01-01 |
| e249 | cc3_2_1_2 | finance | 2026-01-01 |
| e249 | cc3_2_1_2 | hr | 2026-01-01 |
| e250 | cc3_2_1_2 | finance | 2026-01-01 |
| e250 | cc3_2_1_2 | hr | 2026-01-01 |
| e251 | cc3_2_1_3 | finance | 2026-01-01 |
| e251 | cc3_2_1_3 | hr | 2026-01-01 |
| e251 | cc3_2_3_2 | hr | 2026-08-09 |
| e252 | cc3_2_1_3 | finance | 2026-01-01 |
| e252 | cc3_2_1_3 | hr | 2026-01-01 |
| e252 | cc3_2_3_2 | hr | 2026-06-23 |
| e253 | cc3_2_2_1 | finance | 2026-01-01 |
| e253 | cc3_2_2_1 | hr | 2026-01-01 |
| e254 | cc3_2_2_1 | finance | 2026-01-01 |
| e254 | cc3_2_2_1 | hr | 2026-01-01 |
| e255 | cc3_2_2_2 | finance | 2026-01-01 |
| e255 | cc3_2_2_2 | hr | 2026-01-01 |
| e255 | cc2_3_1_3 | hr | 2026-07-05 |
| e256 | cc3_2_2_2 | finance | 2026-01-01 |
| e256 | cc3_2_2_2 | hr | 2026-01-01 |
| e257 | cc3_2_2_3 | finance | 2026-01-01 |
| e257 | cc3_2_2_3 | hr | 2026-01-01 |
| e258 | cc3_2_2_3 | finance | 2026-01-01 |
| e258 | cc3_2_2_3 | hr | 2026-01-01 |
| e259 | cc3_2_3_1 | finance | 2026-01-01 |
| e259 | cc3_2_3_1 | hr | 2026-01-01 |
| e260 | cc3_2_3_1 | finance | 2026-01-01 |
| e260 | cc3_2_3_1 | hr | 2026-01-01 |
| e261 | cc3_2_3_2 | finance | 2026-01-01 |
| e261 | cc3_2_3_2 | hr | 2026-01-01 |
| e262 | cc3_2_3_2 | finance | 2026-01-01 |
| e262 | cc3_2_3_2 | hr | 2026-01-01 |
| e263 | cc3_2_3_3 | finance | 2026-01-01 |
| e263 | cc3_2_3_3 | hr | 2026-01-01 |
| e264 | cc3_2_3_3 | finance | 2026-01-01 |
| e264 | cc3_2_3_3 | hr | 2026-01-01 |
| e265 | cc3_3_1_1 | finance | 2026-01-01 |
| e265 | cc3_2_2_3 | finance | 2026-08-07 |
| e265 | cc3_3_1_1 | hr | 2026-01-01 |
| e265 | cc3_2_2_3 | hr | 2026-07-04 |
| e266 | cc3_3_1_1 | finance | 2026-01-01 |
| e266 | cc3_3_1_1 | hr | 2026-01-01 |
| e267 | cc3_3_1_2 | finance | 2026-01-01 |
| e267 | cc3_3_1_2 | hr | 2026-01-01 |
| e268 | cc3_3_1_2 | finance | 2026-01-01 |
| e268 | cc3_3_1_2 | hr | 2026-01-01 |
| e269 | cc3_3_1_3 | finance | 2026-01-01 |
| e269 | cc3_3_1_3 | hr | 2026-01-01 |
| e270 | cc3_3_1_3 | finance | 2026-01-01 |
| e270 | cc3_3_1_3 | hr | 2026-01-01 |
| e271 | cc3_3_2_1 | finance | 2026-01-01 |
| e271 | cc3_3_2_1 | hr | 2026-01-01 |
| e271 | cc3_2_2_1 | hr | 2026-07-31 |
| e272 | cc3_3_2_1 | finance | 2026-01-01 |
| e272 | cc3_3_2_1 | hr | 2026-01-01 |
| e273 | cc3_3_2_2 | finance | 2026-01-01 |
| e273 | cc3_3_2_2 | hr | 2026-01-01 |
| e274 | cc3_3_2_2 | finance | 2026-01-01 |
| e274 | cc3_3_2_2 | hr | 2026-01-01 |
| e275 | cc3_3_2_3 | finance | 2026-01-01 |
| e275 | cc3_3_2_3 | hr | 2026-01-01 |
| e276 | cc3_3_2_3 | finance | 2026-01-01 |
| e276 | cc3_3_2_3 | hr | 2026-01-01 |
| e277 | cc3_3_3_1 | finance | 2026-01-01 |
| e277 | cc3_3_3_1 | hr | 2026-01-01 |
| e278 | cc3_3_3_1 | finance | 2026-01-01 |
| e278 | cc3_3_3_1 | hr | 2026-01-01 |
| e279 | cc3_3_3_2 | finance | 2026-01-01 |
| e279 | cc3_3_3_2 | hr | 2026-01-01 |
| e280 | cc3_3_3_2 | finance | 2026-01-01 |
| e280 | cc3_3_3_2 | hr | 2026-01-01 |
| e281 | cc3_3_3_3 | finance | 2026-01-01 |
| e281 | cc3_3_3_3 | hr | 2026-01-01 |
| e282 | cc3_3_3_3 | finance | 2026-01-01 |
| e282 | cc3_3_3_3 | hr | 2026-01-01 |

## exemption

An exemption from the cap check for one request category, granted on a date.
Identified by: exemption.

| exemption | category | granted |
|---|---|---|
| capex | capital | 2026-01-01 |

## exemption_withdrawn

The date an exemption was withdrawn; it no longer applies from that date on.
Identified by: exemption. References: `exemption` refers to `exemption`.

| exemption | date |
|---|---|
| capex | 2026-08-10 |

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
- **R201.** A request's dated rules (approval limits, vendor status, exemptions) are read as of the date the request was raised.
- **R202.** A role's approval limit on a date is the limit of the version valid on that date.
- **R203.** A vendor's status on a date is the status of the period that contains that date.
- **R204.** A request's vendor is approved for it if the vendor's status on the request's governing date is approved.
- **R205.** According to a source, an employee belongs on a date to the cost centre of that source's latest assignment record effective on or before that date.
- **R206.** An employee's cost centre is disputed on a date if hr and finance place them in different cost centres on that date.
- **R207.** An exemption is in force on a date if it was granted on or before that date and not withdrawn on or before that date.

# Decisions

Questions of interpretation, who decides them, and what was decided. The definitions above already follow these decisions.

- **c1** (owner: controller), on committed spend: Does the committed spend of a cost centre include pending requests? Decided: booked_only.
- **c2** (owner: procurement), on governing date: Which date governs a request's dated rules (approval limits, vendor status, exemptions), the request date or today? Decided: request_date.
- **c3** (owner: hr), on department: Is an employee's department their cost centre or their cost centre's organisational unit? Decided: cost_centre.
- **c4** (owner: controller), on cap scope: Does a request's cap check cover only the requester's cost centre, or also every ancestor of it? Decided: with_ancestors.
- **c6** (owner: controller), on booked total: Does the booked total of a cost centre include what is booked on its descendants, or only what is booked directly on it? Decided: with_descendants.
