const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "faq",

  run: async (client, message, args) => {
    if (message.author.id !== '1297729779105009725') return;

    const embed = new Discord.MessageEmbed()
      .setAuthor(`root`, message.author.avatarURL())
      .setImage('https://cdn.discordapp.com/attachments/870209468443533353/871177546446811166/bleed_banner.png')
      .setTitle(`Getting started with root`)
      .setDescription(`Learn how to set up root in your server or enhance your everyday use with commands & more.\nBy default, in a server with root, the prefix for the bot is a comma ,.`)
      .addField(`**Hey There,**`, `\u3000Welcome to the support server for root, a multi-purpose Discord bot fitting all communities with an easy-to-use system. This is the landing page to help you get set up and explaining all the commands you need to know.`)
      .addField(`**Why Root?**`, `Root is a sophisticated bot. Unlike many bots, root focuses on a smooth theme, with ease of access to a wide range of commands that may require multiple bots for. Some of it's notable features include Altdentifier, Autorole,  Modlogs, Custom Prefixes and Welcome Messages, also an easy-to-use embed feature. It's the ultimate all in one Discord bot for all servers.`)
      .addField(`**FAQ**`, `Please reach out to **7axq** on Discord for priority replies. Additionally, you can join the [support server](https://discord.gg/E5vPHzFU2S) and send a message in the main channel which will automatically alert us.
  If you are not in the support server or would like an alternative option, you may use ,help in any guild, and root will DM you so you can submit your request and contact the developers through the bot.
Alternatively, direct message four#0001 with your request.`)
      .setColor(color)
      .setFooter('root bot')
      .setTimestamp()
    return message.channel.send(embed)
  }
}