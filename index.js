import { Bot } from "grammy";
import "dotenv/config";
import express from "express";

const bot = new Bot(process.env.BOT_TOKEN);

// === Serveur web pour la page cashback ===
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/cashback", (req, res) => {
  res.sendFile(new URL("./cashback.html", import.meta.url).pathname);
});

app.get("/", (req, res) => {
  res.send("🤖 Bot Telegram actif — va sur /cashback");
});

app.listen(PORT, () => {
  console.log(`🌐 Page cashback dispo sur http://localhost:${PORT}/cashback`);
});

// === Ton bot Telegram ===
bot.on("message", (ctx) => ctx.reply("Salut, ça marche ! ✅"));

bot.start();
console.log("✅ Bot lancé");
