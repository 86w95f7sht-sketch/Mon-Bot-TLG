import { Bot } from "grammy";
import "dotenv/config";

const bot = new Bot(process.env.BOT_TOKEN);

bot.on("message", (ctx) => ctx.reply("Salut, ça marche ! ✅"));

bot.start();
console.log("✅ Bot lancé");
