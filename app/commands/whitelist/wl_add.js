const {SlashCommandBuilder} = require('discord.js');
const Database = require('better-sqlite3');
const db = new Database("whitelist.sqlite");



module.exports = {

    data : new SlashCommandBuilder()
        .setName('wl_add')
        .setDescription('Add an user to the whitelist')
        .addStringOption(option => option.setName('user').setDescription('The user to add to the whitelist').setRequired(true))
        .addStringOption(option => option.setName('id').setDescription('The id of the user').setRequired(true)),


    async execute(interaction) {

        let user = interaction.options.getString('user');
        let id = interaction.options.getString('id');

        const check = db.prepare(`SELECT * FROM users WHERE userID = ${id}`);
        const resultCheck = check.get();
        
        if (resultCheck === undefined) {
            const query = db.prepare(`INSERT INTO users (userID, nickname, status) VALUES ('${id}','${user}','wl')`);
            const result = query.run();
            console.log(result);
            await interaction.reply({content: `The user ${user} has been added to the whitelist`});
        } else {
            await interaction.reply({content: `The user ${user} is already in the whitelist`});
        }
        
    }
};