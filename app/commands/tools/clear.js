const {SlashCommandBuilder} = require('discord.js');
const Database = require('better-sqlite3');
const db = new Database("whitelist.sqlite");



module.exports = {

    data : new SlashCommandBuilder()
        .setName('clear')
        .setDescription('Nettoie le channel des messages')
        .addIntegerOption(option => option.setName('nombre').setDescription('The user to add to the whitelist').setRequired(true)),

    async execute(interaction) {

        let nombre = interaction.options.getInteger('nombre');
        
        await interaction.channel.bulkDelete(nombre);
        await interaction.reply({content: `${nombre} messages supprimés.`});
    }

    
};