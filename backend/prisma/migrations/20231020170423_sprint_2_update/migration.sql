/*
  Warnings:

  - You are about to drop the column `createdById` on the `Rating` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[appointmentId]` on the table `Rating` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `appointmentId` to the `Rating` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Rating" DROP COLUMN "createdById",
ADD COLUMN     "appointmentId" TEXT NOT NULL;

-- CreateTable
CREATE TABLE "Document" (
    "id" TEXT NOT NULL,
    "tutorId" TEXT NOT NULL,
    "document" TEXT NOT NULL,

    CONSTRAINT "Document_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Rating_appointmentId_key" ON "Rating"("appointmentId");

-- AddForeignKey
ALTER TABLE "Document" ADD CONSTRAINT "Document_tutorId_fkey" FOREIGN KEY ("tutorId") REFERENCES "Tutor"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Rating" ADD CONSTRAINT "Rating_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES "Appointment"("id") ON DELETE CASCADE ON UPDATE CASCADE;
