/*
  Warnings:

  - You are about to drop the column `email` on the `Admin` table. All the data in the column will be lost.
  - You are about to drop the column `hashedPassword` on the `Admin` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Admin` table. All the data in the column will be lost.
  - You are about to drop the column `bio` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `email` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `hashedPassword` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `location` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `phoneNumber` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `profilePicture` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `bio` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `email` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `hashedPassword` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `location` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `phoneNumber` on the `Tutor` table. All the data in the column will be lost.
  - You are about to drop the column `profilePicture` on the `Tutor` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[userInfoId]` on the table `Admin` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[userInfoId]` on the table `Student` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[userInfoId]` on the table `Tutor` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `userInfoId` to the `Admin` table without a default value. This is not possible if the table is not empty.
  - Added the required column `userInfoId` to the `Student` table without a default value. This is not possible if the table is not empty.
  - Added the required column `userInfoId` to the `Tutor` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "Appointment" DROP CONSTRAINT "Appointment_studentId_fkey";

-- DropForeignKey
ALTER TABLE "Appointment" DROP CONSTRAINT "Appointment_tutorId_fkey";

-- DropForeignKey
ALTER TABLE "Rating" DROP CONSTRAINT "Rating_tutorId_fkey";

-- DropForeignKey
ALTER TABLE "TutorAvailability" DROP CONSTRAINT "TutorAvailability_tutorId_fkey";

-- DropIndex
DROP INDEX "Admin_email_key";

-- DropIndex
DROP INDEX "Student_email_key";

-- DropIndex
DROP INDEX "Tutor_email_key";

-- AlterTable
ALTER TABLE "Admin" DROP COLUMN "email",
DROP COLUMN "hashedPassword",
DROP COLUMN "name",
ADD COLUMN     "userInfoId" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Student" DROP COLUMN "bio",
DROP COLUMN "email",
DROP COLUMN "hashedPassword",
DROP COLUMN "location",
DROP COLUMN "name",
DROP COLUMN "phoneNumber",
DROP COLUMN "profilePicture",
ADD COLUMN     "userInfoId" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Tutor" DROP COLUMN "bio",
DROP COLUMN "email",
DROP COLUMN "hashedPassword",
DROP COLUMN "location",
DROP COLUMN "name",
DROP COLUMN "phoneNumber",
DROP COLUMN "profilePicture",
ADD COLUMN     "userInfoId" TEXT NOT NULL;

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "hashedPassword" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "bio" TEXT,
    "profilePicture" TEXT,
    "location" TEXT,
    "phoneNumber" TEXT,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Admin_userInfoId_key" ON "Admin"("userInfoId");

-- CreateIndex
CREATE UNIQUE INDEX "Student_userInfoId_key" ON "Student"("userInfoId");

-- CreateIndex
CREATE UNIQUE INDEX "Tutor_userInfoId_key" ON "Tutor"("userInfoId");

-- AddForeignKey
ALTER TABLE "Admin" ADD CONSTRAINT "Admin_userInfoId_fkey" FOREIGN KEY ("userInfoId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Student" ADD CONSTRAINT "Student_userInfoId_fkey" FOREIGN KEY ("userInfoId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tutor" ADD CONSTRAINT "Tutor_userInfoId_fkey" FOREIGN KEY ("userInfoId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TutorAvailability" ADD CONSTRAINT "TutorAvailability_tutorId_fkey" FOREIGN KEY ("tutorId") REFERENCES "Tutor"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Rating" ADD CONSTRAINT "Rating_tutorId_fkey" FOREIGN KEY ("tutorId") REFERENCES "Tutor"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Appointment" ADD CONSTRAINT "Appointment_tutorId_fkey" FOREIGN KEY ("tutorId") REFERENCES "Tutor"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Appointment" ADD CONSTRAINT "Appointment_studentId_fkey" FOREIGN KEY ("studentId") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;
