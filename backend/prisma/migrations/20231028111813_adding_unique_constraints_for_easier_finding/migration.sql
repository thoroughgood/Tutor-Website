/*
  Warnings:

  - A unique constraint covering the columns `[id,tutorId]` on the table `Appointment` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[id,studentId]` on the table `Appointment` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[id,tutorId]` on the table `Document` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[id,appointmentId]` on the table `Rating` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[id,tutorId]` on the table `Rating` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[tutorId,appointmentId]` on the table `Rating` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[id,tutorId]` on the table `TutorAvailability` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "Appointment_id_tutorId_key" ON "Appointment"("id", "tutorId");

-- CreateIndex
CREATE UNIQUE INDEX "Appointment_id_studentId_key" ON "Appointment"("id", "studentId");

-- CreateIndex
CREATE UNIQUE INDEX "Document_id_tutorId_key" ON "Document"("id", "tutorId");

-- CreateIndex
CREATE UNIQUE INDEX "Rating_id_appointmentId_key" ON "Rating"("id", "appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "Rating_id_tutorId_key" ON "Rating"("id", "tutorId");

-- CreateIndex
CREATE UNIQUE INDEX "Rating_tutorId_appointmentId_key" ON "Rating"("tutorId", "appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "TutorAvailability_id_tutorId_key" ON "TutorAvailability"("id", "tutorId");
