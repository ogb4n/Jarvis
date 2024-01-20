const {SlashCommandBuilder} = require('discord.js');
const Database = require('better-sqlite3');
const db = new Database("whitelist.sqlite");



module.exports = {

    data : new SlashCommandBuilder()
        .setName('ban')
        .setDescription('Nettoie le channel des messages')
        .addStringOption(option => option.setName('user').setDescription("L'utilisateur à bannir.").setRequired(true))
        .addStringOption(option => option.setName('raison').setDescription("La raison du ban.").setRequired(false)),

    async execute(interaction) {

        let raison = interaction.options.getString('raison');
        let user = interaction.options.getString('user');
        const regex = new RegExp('^[0-9]+$');

        if ( user.match(regex) === null ) {
            await interaction.reply({content: "Vous devez entrer un UserID."});

        } else {

            const query = db.prepare(`UPDATE users SET status = 'banni' WHERE userID = ${user}`);
            const result = query.run();
            
            await interaction.guild.members.ban(user, {reason: raison});
            await interaction.reply({content: `L'utilisateur <@${user}> a été banni.`});
        }
    }
};