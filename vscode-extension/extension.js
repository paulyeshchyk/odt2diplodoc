// vscode-extension/extension.js
const vscode = require('vscode');
const path = require('path');
const { initNls } = require('./nls_loader');

/**
 * Возвращает корневую папку рабочей области.
 * @param {vscode.Uri} [uri]  
 * @returns {string}
 */
function getWorkspaceRoot(uri) {
    const folder = vscode.workspace.workspaceFolders?.[0];
    if (folder) return folder.uri.fsPath;
    if (uri) return path.dirname(uri.fsPath);
    return process.cwd();
}

/**
 * Путь к папке python внутри расширения.
 * @param {vscode.ExtensionContext} context
 * @returns {string}
 */
function getPythonDir(context) {
    return path.join(context.extensionPath, 'python');
}

/** 
 * @typedef {Object} TerminalOptions
 * @property {string} terminalName
 * @property {string} cwd
 */

/**
 * Путь к папке lua внутри расширения.
 * @param {vscode.ExtensionContext} context
 * @returns {string}
 */
function getLuaDir(context) {
    return path.join(context.extensionPath, 'lua');
}

/**
 * Запускает Python-скрипт в терминале VSCode с правильным PYTHONPATH.
 * @param {vscode.ExtensionContext} context
 * @param {string} scriptPath – абсолютный путь к скрипту
 * @param {string[]} args – массив аргументов командной строки
 * @param {TerminalOptions} options – { cwd: string, terminalName: string }
 */
async function runPythonScript(context, scriptPath, args, options) {
    const pythonDir = getPythonDir(context);
    const terminal = vscode.window.createTerminal({
        name: options.terminalName,
        cwd: options.cwd,
    });
    terminal.show();

    const pythonPathCmd = `$env:PYTHONPATH = "${pythonDir}"`;
    const quotedArgs = args.map(arg => `"${arg}"`).join(' ');
    const pythonCmd = `python "${scriptPath}" ${quotedArgs}`;
    const fullCmd = `${pythonPathCmd}; ${pythonCmd}`;

    console.log(`[Diplodoc] Запуск: ${fullCmd}`);
    terminal.sendText(fullCmd);
}

/**
 * Активация расширения: регистрация команд.
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Diplodoc Converter extension is now active!');

    const locale = vscode.env.language;
    const rootPath = context.extensionPath;
    initNls(locale, rootPath);

    // Команда: сборка ODT из MD-иерархии
    const buildOdt = vscode.commands.registerCommand('diplodoc.buildOdt', async (uri) => {
        let inputDir = uri ? uri.fsPath : await vscode.window.showInputBox({
            prompt: 'Путь к корневой папке документации (содержит toc.yaml)'
        });
        if (!inputDir) return;

        const outputFile = await vscode.window.showSaveDialog({
            title: 'Сохранить ODT как...',
            filters: { 'ODT files': ['odt'] }
        });
        if (!outputFile) return;

        const workspaceRoot = getWorkspaceRoot(uri);
        const scriptPath = path.join(getPythonDir(context), 'diplodoc_converter', 'intoODT', 'cli.py');
        const args = ['--input-dir', inputDir, '--output', outputFile.fsPath];
        await runPythonScript(context, scriptPath, args, {
            cwd: workspaceRoot,
            terminalName: 'Build ODT from MD'
        });
    });

    // Команда: импорт ODT в Diplodoc
    const importOdt = vscode.commands.registerCommand('diplodoc.importOdt', async (uri) => {
        const odtPath = uri.fsPath;
        const workspaceRoot = getWorkspaceRoot(uri);
        const cliPath = path.join(getPythonDir(context), 'diplodoc_converter', 'cli.py');

        const outputDir = await vscode.window.showInputBox({
            prompt: 'Папка для результата (output)',
            value: path.join(path.dirname(odtPath), 'docs'),
        });
        if (!outputDir) return;

        const useCache = await vscode.window.showQuickPick(['Да (с кэшем)', 'Нет (чистый запуск)'], {
            placeHolder: 'Использовать кэш?'
        });
        if (!useCache) return;

        const luaFilters = await vscode.window.showInputBox({
            prompt: 'Lua-фильтры (через запятую)',
            value: 'no-img-size.lua'
        });
        if (!luaFilters) return;

        const maxLevel = await vscode.window.showInputBox({
            prompt: 'Максимальный уровень заголовка',
            value: '6'
        });
        if (!maxLevel) return;

        const args = [odtPath, outputDir, '--max-heading-level', maxLevel];
        if (useCache === 'Да (с кэшем)') {
            args.push('--reuse-cache', '--keep-cache');
        }
        args.push('--enable-crossref');
        args.push('--lua-filter', luaFilters);
        args.push('--lua-dir', getLuaDir(context));

        await runPythonScript(context, cliPath, args, {
            cwd: workspaceRoot,
            terminalName: 'Diplodoc Converter'
        });
    });

    context.subscriptions.push(buildOdt, importOdt);
}

function deactivate() { }

module.exports = { activate, deactivate };