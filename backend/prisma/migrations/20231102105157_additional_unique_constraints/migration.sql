/*
  Warnings:

  - A unique constraint covering the columns `[id,appointmentId]` on the table `Notification` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[appointmentId,userId]` on the table `Notification` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "Notification_id_appointmentId_key" ON "Notification"("id", "appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "Notification_appointmentId_userId_key" ON "Notification"("appointmentId", "userId");
