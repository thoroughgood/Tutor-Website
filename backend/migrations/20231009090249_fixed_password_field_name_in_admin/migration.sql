/*
  Warnings:

  - You are about to drop the column `hashed_password` on the `Admin` table. All the data in the column will be lost.
  - Added the required column `hashedPassword` to the `Admin` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Admin" DROP COLUMN "hashed_password",
ADD COLUMN     "hashedPassword" TEXT NOT NULL;
