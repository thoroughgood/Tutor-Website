/*
  Warnings:

  - A unique constraint covering the columns `[appointmentId,tutorId]` on the table `Rating` will be added. If there are existing duplicate values, this will fail.

*/
-- DropIndex
DROP INDEX "Rating_tutorId_appointmentId_key";

-- CreateTable
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "sentTime" TIMESTAMP(3) NOT NULL,
    "content" TEXT NOT NULL,
    "sentById" TEXT NOT NULL,
    "appointmentId" TEXT,
    "directMessageId" TEXT,

    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DirectMessage" (
    "id" TEXT NOT NULL,
    "fromUserId" TEXT NOT NULL,
    "otherUserId" TEXT NOT NULL,

    CONSTRAINT "DirectMessage_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Message_id_sentById_key" ON "Message"("id", "sentById");

-- CreateIndex
CREATE UNIQUE INDEX "Message_id_appointmentId_key" ON "Message"("id", "appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "Message_id_directMessageId_key" ON "Message"("id", "directMessageId");

-- CreateIndex
CREATE UNIQUE INDEX "Message_sentById_appointmentId_key" ON "Message"("sentById", "appointmentId");

-- CreateIndex
CREATE UNIQUE INDEX "Message_sentById_directMessageId_key" ON "Message"("sentById", "directMessageId");

-- CreateIndex
CREATE UNIQUE INDEX "DirectMessage_id_fromUserId_key" ON "DirectMessage"("id", "fromUserId");

-- CreateIndex
CREATE UNIQUE INDEX "DirectMessage_id_otherUserId_key" ON "DirectMessage"("id", "otherUserId");

-- CreateIndex
CREATE UNIQUE INDEX "DirectMessage_fromUserId_otherUserId_key" ON "DirectMessage"("fromUserId", "otherUserId");

-- CreateIndex
CREATE UNIQUE INDEX "Rating_appointmentId_tutorId_key" ON "Rating"("appointmentId", "tutorId");

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_sentById_fkey" FOREIGN KEY ("sentById") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES "Appointment"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_directMessageId_fkey" FOREIGN KEY ("directMessageId") REFERENCES "DirectMessage"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DirectMessage" ADD CONSTRAINT "DirectMessage_fromUserId_fkey" FOREIGN KEY ("fromUserId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DirectMessage" ADD CONSTRAINT "DirectMessage_otherUserId_fkey" FOREIGN KEY ("otherUserId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
