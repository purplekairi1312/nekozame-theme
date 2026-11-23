/*
 * nekozame for OpenWebRX+. generated from palette.toml by generate.py; edit the palette there.
 * a UI theme and a waterfall theme, both the default until someone picks
 * another one in the receiver's settings.
 */

$('#openwebrx-themes-listbox').append($('<option>').val('nekozame').text('nekozame'));
$('#openwebrx-wf-themes-listbox').append($('<option>').val('nekozame').text('nekozame'));

// weak to strong signals: a near-black violet for the noise, then deep violet,
// grape, lilac, pink, butter and white
UI.wfThemes['nekozame'] = [
    '#1e1828', '{{deep}}', '{{selection}}', '{{violet}}', '{{orchid}}', '{{butter}}', '#ffffff'
].map(function (h) { return parseInt(h.slice(1), 16); });

// the server's default ("Gray") becomes nekozame
var nekozameDefault = UI.setDefaultTheme;
UI.setDefaultTheme = function (theme) {
    return nekozameDefault.call(this, (!theme || theme === 'default') ? 'nekozame' : theme);
};

if (!LS.has('ui_theme')) UI.setTheme('nekozame');
if (!LS.has('wf_theme')) UI.setWfTheme('nekozame');

Plugins.nekozame._version = 1.0;
