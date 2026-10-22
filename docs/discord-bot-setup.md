# Discord Bot Setup

This guide creates the bot's Discord account, turns on the permission it needs to read photos, gets its token (its secret password), and invites it to your server. You do all of this by clicking on the Discord website. No code is needed.

Do `docs/discord-server-setup.md` first, because you need your server before you can invite the bot to it.

Discord changes its screens from time to time, so a button may look slightly different. The names in **bold** are what to look for.

---

## ⚠️ READ THIS FIRST: the bot token is a password

The **bot token** is a long string of letters and numbers. Anyone who has it can log in as your bot, post as it, and read everything it can read.

- **Never share it** with anyone, in any message or email.
- **Never paste it into this chat** (or any chat with an AI assistant). Chat text can be stored and logged.
- **Never commit it.** It goes only in your local `.env` file, which is already listed in `.gitignore` so git skips it. It must never appear in any file that is committed, or on GitHub, because everything on GitHub is public and permanent.
- **Never put it in a screenshot**, a document, or a shared folder.

**If you think it leaked (even once):** go straight to Part 3, click **Reset Token**, and copy the new one. The old token stops working the moment you reset it, so a leaked token becomes useless.

---

## Part 1 – Create the application and bot

In Discord, an **application** is the registration for something you build, and the **bot** is the account that belongs to it.

1. Open a web browser and go to https://discord.com/developers/applications
2. If asked, log in with the same Discord account that owns your server.
3. Click the **New Application** button (top right).
4. In **Name**, type a name for your bot, for example `Vehicle Photo Agent`. This is the name people will see in the channel.
5. Tick the box to accept Discord's **Terms of Service** and Developer Policy.
6. Click **Create**.

You are now on your application's page, with a menu down the left side.

(Optional) On the **General Information** page you can add a picture and a description. You can skip this.

---

## Part 2 – Turn on Message Content Intent

**Why this is needed.** Discord treats message contents as private data, so a bot receives them only if you switch on a special permission, called an **intent**. Without **Message Content Intent**, the bot would not be told what is inside a message. The agent needs it to see the photo attachments, and to copy the poster's typed note into the log. If it is off, the bot can connect, but it will fail to read photos. If you see an error such as `Privileged intent provided is not enabled`, this switch is the cause.

1. In the left menu of your application page, click **Bot**.
2. Scroll down to the section called **Privileged Gateway Intents**.
3. Find **Message Content Intent**.
4. Click its switch so it turns on (blue or green).
5. Leave **Presence Intent** and **Server Members Intent** switched **off**. The agent doesn't need them.
6. If a bar appears at the bottom saying you have unsaved changes, click **Save Changes**.

---

## Part 3 – Get the bot token

Read the warning at the top of this guide before you do this part.

1. Still on the **Bot** page, scroll up to the section that shows the bot's name.
2. Find the **Token** area and click **Reset Token**.
3. A box asks you to confirm. Click **Yes, do it!**.
4. If Discord asks for your password or two-step code, enter it.
5. The token appears **once**. Click **Copy**.
6. Open **Notepad** (press the Windows key, type `Notepad`, press Enter).
7. Press **Ctrl + V** to paste it, and save the file in a private place on your own computer, outside the project folder, for example `C:\Users\User\Documents\private\bot-token.txt`.

**Check:**
- The token is shown only once. If you lose it, repeat steps 2 to 7 to make a new one. The old one stops working.
- You will paste it into a `.env` file later, when the code is written. You don't need to do that yet.

---

## Part 4 – Stop other people from adding your bot

1. Still on the **Bot** page, find the switch **Public Bot**.
2. Turn it **off**.
3. Leave **Requires OAuth2 Code Grant** switched **off**.
4. If a bar appears at the bottom, click **Save Changes**.

With **Public Bot** off, only you (the owner of the application) can invite the bot to servers. This keeps strangers from adding it elsewhere and using your Claude allowance.

---

## Part 5 – Choose the permissions

The bot should have only what it needs.

| Permission | Needed? | Why |
|---|---|---|
| **View Channels** | Yes | To see the `vehicle-photos` channel and the photos in it. |
| **Read Message History** | Yes | To reply to a specific message. |
| **Send Messages** | Yes | To post its replies. |
| **Add Reactions** | Yes | To add and remove the ⏳ reaction. |
| **Attach Files** | **No** | The bot only sends text. Leave it off. |
| **Administrator** and everything else | **No** | Never give more than needed. |

---

## Part 6 – Invite the bot to your server

1. In the left menu of your application page, click **OAuth2**.
2. Scroll down to the **OAuth2 URL Generator** section. (In some versions it is a separate menu item named **URL Generator** under **OAuth2**.)
3. Under **Scopes**, tick **bot**. Leave every other scope unticked.
4. A new section named **Bot Permissions** appears below. Tick these four boxes only:
   - **View Channels**
   - **Send Messages**
   - **Read Message History**
   - **Add Reactions**
5. Leave all the other boxes unticked, especially **Attach Files** and **Administrator**.
6. Scroll to the bottom to the **Generated URL** box.
7. Click **Copy**.
8. Paste the link into your web browser's address bar and press **Enter**.
9. In the **Add to server** drop-down, choose your server (for example `Vehicle Spotters`).
10. Click **Continue**.
11. Check that the four permissions listed are the ones you ticked, then click **Authorize**.
12. If Discord shows a "Are you human?" check, complete it.

The generated link is not secret: it can only add the bot to a server, and because **Public Bot** is off, only you can use it. It is not the same as the token.

---

## Part 7 – Check that it worked

1. Go back to the Discord app and open your server.
2. In the member list on the right, look for your bot. It will have a **BOT** tag and will probably show as **offline**. That is normal, because the program isn't running yet.
3. Click the `vehicle-photos` channel. A message such as "Vehicle Photo Agent joined the server" may appear.

**If you made `vehicle-photos` a Private Channel:** the bot cannot see it yet.

1. Right-click the channel and click **Edit Channel**.
2. Click **Permissions**.
3. Under **Roles/Members**, click the **+** and choose the bot (or the bot's role, named the same as the bot).
4. Make sure **View Channel**, **Send Messages**, **Read Message History** and **Add Reactions** are switched to the green tick.
5. Click **Save Changes**.

---

## What you will have, and what happens next

| Item | Where it is | Secret? |
|---|---|---|
| `CHANNEL_ID` | Your Notepad file from the server guide | No |
| `DISCORD_TOKEN` | Your private Notepad file | **Yes, never share or commit** |
| Bot in your server | Shown offline | No |

When the code is written, you will create a file called `.env` in the project folder with the four settings (`DISCORD_TOKEN`, `CHANNEL_ID`, `CLAUDE_MODEL`, `DATA_DIR`). The token goes there and nowhere else.

---

## Checklist

- [ ] The application exists in the Developer Portal.
- [ ] **Message Content Intent** is on, and saved.
- [ ] You have the bot token saved privately, and have not shared or pasted it anywhere else.
- [ ] **Public Bot** is off.
- [ ] You invited the bot with only the four permissions: View Channels, Send Messages, Read Message History, Add Reactions.
- [ ] The bot shows in your server's member list (offline for now).
- [ ] Only a private, local file holds the token. No committed file holds it.
