const fs = require("node:fs");
const path = require("node:path");
const Database = require('better-sqlite3');
const fetch = require("node-fetch");
const { Client, Partials, Collection, Events, GatewayIntentBits, EmbedBuilder, Guild, GuildMember, ActivityType } = require("discord.js");
const { ReactionRole } = require("discordjs-reaction-role");
const spawn = require("child_process").spawn;
const { channel } = require("node:diagnostics_channel");
const { exec } = require('child_process');
const { get } = require("node:http");
const db = new Database("whitelist.sqlite");
require("dotenv").config();


/// this is the base configuration for each bot, starting 

// CLIENT JARVIS
const client = new Client({
	partials: [Partials.Message, Partials.Reaction],
	intents: [
	  GatewayIntentBits.Guilds,
	  GatewayIntentBits.GuildMessages,
	  GatewayIntentBits.GuildMessageReactions,
	],
});
// BOT ETH
const eth_pricebot = new Client({
	partials: [Partials.Message, Partials.Reaction],
	intents: [
	  GatewayIntentBits.Guilds,
	  GatewayIntentBits.GuildMessages,
	  GatewayIntentBits.GuildMessageReactions,
	],
});
// BOT SOL
const sol_pricebot = new Client({
	partials: [Partials.Message, Partials.Reaction],
	intents: [
	  GatewayIntentBits.Guilds,
	  GatewayIntentBits.GuildMessages,
	  GatewayIntentBits.GuildMessageReactions,
	],
});
// BOT BTC
const btc_pricebot = new Client({
	partials: [Partials.Message, Partials.Reaction],
	intents: [
	  GatewayIntentBits.Guilds,
	  GatewayIntentBits.GuildMessages,
	  GatewayIntentBits.GuildMessageReactions,
	],
});
// BOT XMR
const xmr_pricebot = new Client({
	partials: [Partials.Message, Partials.Reaction],
	intents: [
	  GatewayIntentBits.Guilds,
	  GatewayIntentBits.GuildMessages,
	  GatewayIntentBits.GuildMessageReactions,
	],
});


	// logs declaration for every 
eth_pricebot.once(Events.ClientReady, () => {
	console.log(`Logged in as ${eth_pricebot.user}!`);
});
btc_pricebot.once(Events.ClientReady, () => {
	console.log(`Logged in as ${btc_pricebot.user}!`);
});
sol_pricebot.once(Events.ClientReady, () => {
	console.log(`Logged in as ${sol_pricebot.user}!`);
});
xmr_pricebot.once(Events.ClientReady, () => {
	console.log(`Logged in as ${sol_pricebot.user}!`);
});

// Reaction Role Manager
const rr = new ReactionRole(client, [
	{ messageId: process.env.ROLE_MESSAGE_ID, reaction: "🕵️‍♀️", roleId: process.env.ROLE_CYBER},
	{ messageId: process.env.ROLE_MESSAGE_ID, reaction: "🛠️", roleId: process.env.ROLE_ADMINSYS},
	{ messageId: process.env.ROLE_MESSAGE_ID, reaction: "🧑‍💻", roleId: process.env.ROLE_DEVELOPPEUR},
	{ messageId: process.env.ROLE_MESSAGE_ID, reaction: "🧑‍🎓", roleId: process.env.ROLE_STUDENT},
	{ messageId: process.env.ROLE_MESSAGE_ID, reaction: "🤵", roleId: process.env.ROLE_AUTRE},
  ]);


  /// CVE DSCORD SENDER NOT WORKING

//const sentCVEs = new Set();
// if (fs.existsSync('sentCVEs.json')) {
//   const sentCVEsFile = fs.readFileSync('sentCVEs.json', 'utf8');
//   const sentCVEsArray = JSON.parse(sentCVEsFile);
//   sentCVEsArray.forEach((cve) => {
// 	sentCVEs.add(cve);
//   });
// }

// async function sendCVEInformation(cveInfo, channel) {
//   // Set the color of the embed based on the severity of the CVE
//   	let color = 0x2ecc71;
// 	let tag = '⚠️';
// 	if (cveInfo['Severity'].split(' ')[0] < 6.0) {
// 		color = 0xe67e22;
// 	} else if (cveInfo['Severity'].split(' ')[0] < 8.0 && cveInfo['Severity'].split(' ')[0] >= 6.0) {
// 		color = 0xffa200;
// 		tag = '🔥';
// 	} else if (cveInfo['Severity'].split(' ')[0] < 10.0 && cveInfo['Severity'].split(' ')[0] >= 8.0) {
// 		color = 0xff0000;
// 		tag = '💥';
// 	}

// 	// const embed = new EmbedBuilder()
// 	// 	.setColor(color)

// 	// 	.setTitle(`${tag} ${cveInfo['CVE_ID']} `)
// 	// 	.setURL(cveInfo['Link'])
// 	// 	.setAuthor({name : `- ${cveInfo['Vendor'].slice(1).replace(/,/g , ' / ')}`})

// 	// 	.setDescription(` \`\`\`  ${cveInfo['Description'].join(' ')}\`\`\` `)
// 	// 	.addFields({ name: 'Produits', value: `- ${cveInfo['Product'].slice(1).replace(/,/g , ' / ')}`})

// 	// 	.setFooter({ text: "Date : "+ cveInfo['Date'] });
	
// 	// // const cveKey = `${tag} ${cveInfo['CVE_ID']} `;
// 	// // if (!sentCVEs.has(cveKey)) {
// 	// // 	// Ajouter la CVE à l'ensemble des CVE envoyées
// 	// // 	sentCVEs.add(cveKey);
	
// 	// // 		// Enregistrer l'ensemble mis à jour dans le fichier
// 	// // 	fs.writeFileSync('sentCVEs.json', JSON.stringify(Array.from(sentCVEs)), 'utf8');
	
// 	// 		// Envoyer le message seulement si la CVE n'est pas déjà envoyée
// 	// 	channel.send({ embeds: [embed] });
// 	}

// CALLING A PYTHON SCRIPT WTF ???§ 
async function getCVEInformation() {
	// Replace 'python3' with the appropriate command to run Python on your system
	const pythonProcess = exec('python ../scraper/scrap.py', (error, stdout, stderr) => {
	  if (error) {
		console.error(`Error executing Python script: ${error.message}`);
		return;
	  }
	  try {
		// Parse the JSON output from the Python script
		const cveInformation = JSON.parse(stdout);
		
		if (typeof cveInformation === 'string') {
			cveInformation = JSON.parse(cveInformation);
		  }

		// Output the information to the Discord channel
		const channel = client.channels.cache.get('1175725609964552192')
		cveInformation.forEach((cveInfo) => {
			sendCVEInformation(cveInfo, channel);;
		});
	  } catch (parseError) {
		console.error(`Error parsing JSON: ${parseError.message}`);
	  }
	});
	// ksdkfj
	pythonProcess.on('close', (code) => {
	  console.log(`Scraper exited with code ${code}`);
	});
  }


// Price Update
async function updatePrice(bot, url, channelId) {

    const response = await fetch(url);
    const data = await response.json();
	const guild = bot.guilds.cache.get(process.env.GUILD_ID);
	const member = await guild.members.fetch(bot.user.id);
    const price = parseFloat(data.weightedAvgPrice).toFixed(0);
    const priceChange = parseFloat(data.priceChangePercent);
     let status = 'idle';

	 if (priceChange > 0) {
        status = 'online';
        // console.log('Adding role for positive price change to ' + member.user.username);
        if (member && !member.roles.cache.has(process.env.BULL_ROLE)) {
            member.roles.add(process.env.BULL_ROLE);
            member.roles.remove(process.env.BEAR_ROLE);
        } else { member.roles.add(process.env.BULL_ROLE);}
    } else if (priceChange < 0) {
        status = 'dnd';
        // console.log('Removing role for negative price change to '+ member.user.username);
        if (member && member.roles.cache.has(process.env.BULL_ROLE)) {
            member.roles.remove(process.env.BULL_ROLE);
            member.roles.add(process.env.BEAR_ROLE);
        } else {member.roles.add(process.env.BEAR_ROLE);}
    }

    bot.user.setPresence({
        activities: [{ name: `${priceChange}% || ${price} USDT`, type: ActivityType.Custom }],
        status: status,
    });

    // Optionally, update a specific channel with the information
    // const channel = bot.channels.cache.get(channelId);
    // if (channel) {
    //     channel.send(`Price update for ${url}: ${priceChange}% || ${price} USDT`);
    // }
}

async function UpdatePrice() {
    updatePrice(btc_pricebot, process.env.BTC_URL, process.env.CHANNEL_BITCOIN);
    updatePrice(eth_pricebot, process.env.ETH_URL, process.env.CHANNEL_ETH);
    updatePrice(sol_pricebot, process.env.SOL_URL, process.env.CHANNEL_SOL);
    updatePrice(xmr_pricebot, process.env.XMR_URL, process.env.CHANNEL_XMR);
    console.log('Prices Updated');
}

// Commands Handler 
client.commands = new Collection();
const foldersPath = path.join(__dirname, "commands");
const commandFolders = fs.readdirSync(foldersPath);
for (const folder of commandFolders) {
	const commandsPath = path.join(foldersPath, folder);
	const commandFiles = fs.readdirSync(commandsPath).filter((file) => file.endsWith(".js"));
	for (const file of commandFiles) {
		const filePath = path.join(commandsPath, file);
		const command = require(filePath);
		if ("data" in command && "execute" in command) {
			client.commands.set(command.data.name, command);
		} else {
			console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
		}
	}
}

client.once(Events.ClientReady, () => {
	//reload every commands at startup
	const { exec } = require('child_process');
	exec('node commands_deployment.js', (err, stdout, stderr) => {
		if (err) {
			return;
		}
		console.log(`stdout: ${stdout}`);
		console.log(`stderr: ${stderr}`);
	});

	client.user.setPresence({
		activities: [{ name: `Attend une commande`, type: ActivityType.Custom }],
		status: 'dnd',
	  });

	  UpdatePrice();
	  setInterval(UpdatePrice, 120000);
	  getCVEInformation();
	  setInterval(getCVEInformation, 7200000);

	console.log("J4rvIs est connecté !");
});


client.on(Events.InteractionCreate, async (interaction) => {
	if (!interaction.isChatInputCommand()) return;

	const command = client.commands.get(interaction.commandName);

	if (!command) return;

	try {
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
		if (interaction.replied || interaction.deferred) {
			await interaction.followUp({
				content: "There was an error while executing this command!",
				ephemeral: true,
			});
		} else {
			await interaction.reply({ content: "There was an error while executing this command!", ephemeral: true });
		}
	}
});

// whitelist appliance
client.on("guildMemberAdd", (member) => {
	// setting up query
	const query = db.prepare('SELECT * FROM users WHERE userID = ?');
	// on va cherche le résultat
	const result = query.get(member.user.id);
	console.log(result);
	// check si user est dans la db
	if (result === undefined) {
		// il y est pas, on le kick
		member.kick();
	} else {
		// il y est, on le welcome
		member.send(`Welcome to the server, ${member.displayName}!`);
		member.roles.add(process.env.ROLE_INVITE);
	}
});

//bot init

eth_pricebot.login(process.env.ETH_PRICEBOT);
sol_pricebot.login(process.env.SOL_PRICEBOT);
btc_pricebot.login(process.env.BTC_PRICEBOT);
xmr_pricebot.login(process.env.XMR_PRICEBOT);
client.login(process.env.TOKEN);