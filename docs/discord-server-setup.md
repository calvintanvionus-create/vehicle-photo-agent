# Discord Server Setup

This guide sets up the place where the bot will live: your own Discord server, one channel for the agent, and an invite link for your partner. You do all of this by clicking in Discord. No code is needed.

Discord changes its screens from time to time, so a button may look slightly different. The names in **bold** are what to look for.

**You will end up with**

- Your own Discord server.
- A text channel for the agent.
- The channel's number, called `CHANNEL_ID`. It goes into your `.env` file later.
- An invite link for your partner.

You need a Discord account first. If you don't have one, make one at https://discord.com and log in.

---

## Part 1 – Create your own Discord server

1. Open the Discord app on your computer. (You can also use https://discord.com/app in a browser.)
2. Look at the narrow column of round icons on the far left of the window.
3. Scroll to the bottom of that column and click the green **+** button. Its hover text says **Add a Server**.
4. Click **Create My Own**.
5. When asked what the server is for, click **For me and my friends**.
6. Click in the **Server Name** box and type a name, for example `Vehicle Spotters`.
7. (Optional) Click the picture circle to add a server icon. You can skip this.
8. Click **Create**.

Your server now appears in the left column, and you are its owner.

---

## Part 2 – Turn on Developer Mode

Discord hides the numbers it uses to identify channels. Developer Mode makes a **Copy Channel ID** option appear. You only need to do this once.

1. Look at the bottom-left corner of the Discord window. You will see your name and picture.
2. Click the **gear icon** next to your name. This opens **User Settings**.
3. In the left menu, scroll down and click **Advanced**.
4. Find the switch named **Developer Mode** and click it so it turns on (green).
5. Close the settings window by pressing the **Esc** key.

---

## Part 3 – Create a channel for the agent

A channel is one chat room inside a server. The bot will listen to this one channel and ignore every other.

1. Click your server's icon in the left column.
2. In the channel list, find the heading **Text Channels**.
3. Move your mouse over that heading, then click the **+** that appears at its right.
4. Make sure **Text** is selected as the channel type.
5. In **Channel Name**, type `vehicle-photos`. (Discord makes names lower-case with hyphens.)
6. Leave **Private Channel** switched off for now. (See the note below if you want it on.)
7. Click **Create Channel**.

The new channel appears in the list under **Text Channels**.

> **Why this matters for the bot.** Every photo posted in this channel uses your own Claude allowance (see section 13 of `docs/architecture.md`). Only invite people you trust. If you prefer a **Private Channel**, switch it on in step 6. You must then let the bot into it after it joins (see the end of `docs/discord-bot-setup.md`). The easiest start is to keep it off, since the server is yours and only people you invite can join.

---

## Part 4 – Get the CHANNEL_ID

1. In the channel list, find `vehicle-photos`.
2. **Right-click** it. (Mac: Control-click.)
3. Click **Copy Channel ID**, which is near the bottom of the menu. If you don't see it, go back to Part 2; Developer Mode isn't on.
4. Open **Notepad** (press the Windows key, type `Notepad`, press Enter).
5. Press **Ctrl + V** to paste. You will see a long number such as `1234567890123456789`.
6. Save the Notepad file somewhere you can find it later (for example your Documents folder), named `channel-id.txt`.

This number is your `CHANNEL_ID`. It is not secret, but it must be exact. It is only digits, with no spaces or other characters.

---

## Part 5 – Create an invite link so your partner can join

1. Click your **server name** at the very top of the channel list (the bold name with a small arrow next to it).
2. In the menu that opens, click **Invite People**.
3. At the bottom of the window, click **Edit invite link** (it may look like a small gear icon or a line of grey text under the link).
4. Under **Expire After**, choose **7 days**.
5. Under **Max Number of Uses**, choose **1 use**.
6. Leave **Grant temporary membership** switched off.
7. Click **Generate a New Link**.
8. Click **Copy** next to the link.
9. Send the link to your partner by message or email.

**What your partner does**

1. Click the link, or paste it into a browser.
2. Log in to Discord (or create an account).
3. Click **Accept Invite**.

Your partner is now in your server and can see `vehicle-photos`. They can post a vehicle photo there once the bot is running.

> **Safety tips**
> - A link with 7 days and 1 use stops working after your partner has used it. If someone else grabs it first, you can delete it and make a new one.
> - To see or delete invite links later: click the server name, then **Server Settings**, then **Invites**.
> - Don't post the link in a public place. Everyone who joins can use the channel, and every photo they post spends your Claude allowance.

---

## Checklist

- [ ] Your server exists and appears in the left column.
- [ ] Developer Mode is on.
- [ ] The `vehicle-photos` channel exists.
- [ ] You have saved your `CHANNEL_ID` in a Notepad file.
- [ ] Your partner has the invite link and has joined (or will join).

**Next step:** follow `docs/discord-bot-setup.md` to create the bot and invite it to this server.
