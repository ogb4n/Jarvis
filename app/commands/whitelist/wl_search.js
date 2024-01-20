const {SlashCommandBuilder} = require('discord.js');
const Database = require('better-sqlite3');
const db = new Database("whitelist.sqlite");



module.exports = {

    data : new SlashCommandBuilder()
        .setName('wl_search')
        .setDescription('Add an user to the whitelist')
        .addStringOption(option => option.setName('id').setDescription('The id of the user').setRequired(true))
        .addStringOption(option => option.setName('user').setDescription('The user to add to the whitelist')),


    async execute(interaction) {

        let user = interaction.options.getString('user');
        let id = interaction.options.getString('id');

        const check = db.prepare(`SELECT * FROM users WHERE userID = ${id}`);
        const resultCheck = check.get();
        const account = '<@'+id+'>'
        if (resultCheck === undefined) {
            console.log(resultCheck);
            await interaction.reply({content: `The user ${account} is not whitelisted to the server`});
        } else {
            await interaction.reply({content: `The user ${account} is already whitelisted to the server
            `});
        }
        
    }
};