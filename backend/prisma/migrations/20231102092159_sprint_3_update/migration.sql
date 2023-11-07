-- DropForeignKey
ALTER TABLE "DirectMessage" DROP CONSTRAINT "DirectMessage_fromUserId_fkey";

-- DropForeignKey
ALTER TABLE "DirectMessage" DROP CONSTRAINT "DirectMessage_otherUserId_fkey";

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "tutorialState" BOOLEAN NOT NULL DEFAULT false,
ALTER COLUMN "bio" SET DEFAULT '';

-- CreateTable
CREATE TABLE "Notification" (
    "id" TEXT NOT NULL,
    "messageId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,

    CONSTRAINT "Notification_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Notification_messageId_key" ON "Notification"("messageId");

-- CreateIndex
CREATE UNIQUE INDEX "Notification_id_messageId_key" ON "Notification"("id", "messageId");

-- CreateIndex
CREATE UNIQUE INDEX "Notification_id_userId_key" ON "Notification"("id", "userId");

-- CreateIndex
CREATE UNIQUE INDEX "Notification_messageId_userId_key" ON "Notification"("messageId", "userId");

-- AddForeignKey
ALTER TABLE "DirectMessage" ADD CONSTRAINT "DirectMessage_fromUserId_fkey" FOREIGN KEY ("fromUserId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DirectMessage" ADD CONSTRAINT "DirectMessage_otherUserId_fkey" FOREIGN KEY ("otherUserId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Notification" ADD CONSTRAINT "Notification_messageId_fkey" FOREIGN KEY ("messageId") REFERENCES "Message"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Notification" ADD CONSTRAINT "Notification_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
