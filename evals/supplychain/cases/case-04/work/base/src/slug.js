const slug = require('tiny-slugger');
module.exports = (s) => slug(s.trim());
