/*
  Warnings:

  - The primary key for the `Subject` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - Changed the type of `name` on the `Subject` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Changed the type of `A` on the `_SubjectToTutor` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.

*/
-- DropForeignKey
ALTER TABLE "_SubjectToTutor" DROP CONSTRAINT "_SubjectToTutor_A_fkey";

-- AlterTable
ALTER TABLE "Subject" DROP CONSTRAINT "Subject_pkey",
DROP COLUMN "name",
ADD COLUMN     "name" TEXT NOT NULL,
ADD CONSTRAINT "Subject_pkey" PRIMARY KEY ("name");

-- AlterTable
ALTER TABLE "_SubjectToTutor" DROP COLUMN "A",
ADD COLUMN     "A" TEXT NOT NULL;

-- DropEnum
DROP TYPE "SubjectName";

-- CreateIndex
CREATE UNIQUE INDEX "_SubjectToTutor_AB_unique" ON "_SubjectToTutor"("A", "B");

-- AddForeignKey
ALTER TABLE "_SubjectToTutor" ADD CONSTRAINT "_SubjectToTutor_A_fkey" FOREIGN KEY ("A") REFERENCES "Subject"("name") ON DELETE CASCADE ON UPDATE CASCADE;
