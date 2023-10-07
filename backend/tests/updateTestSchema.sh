#!/bin/bash

cp "../schema.prisma" "./prisma/schema.prisma"
# replace datasource fields
sed -i 's/provider[ \t]*=[ \t]*"postgresql"/provider = "sqlite"/g' "./prisma/schema.prisma"
sed -i 's/url[ \t]*= env("DATABASE_URL")/url      = "file:test.db"/g' "./prisma/schema.prisma"
# additional line 1 comment
sed -i '1s/^/\/\/ Copy of dev schema in the root directory with datasource changed\n\n/' "./prisma/schema.prisma"