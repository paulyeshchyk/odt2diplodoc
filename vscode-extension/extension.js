// vscode-extension/extension.ts
const vscode = require('vscode');
const path = require('path');
const { initNls } = require('./nls_loader');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Diplodoc Converter extension is now active!');

    const locale = vscode.env.language;
    const rootPath = context.extensionPath;

    initNls(locale, rootPath);


    const disposable = vscode.commands.registerCommand('diplodoc.importOdt', async (uri) => {
        const odtPath = uri.fsPath;
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || path.dirname(odtPath);

        const pythonDir = path.join(context.extensionPath, 'python');
        const luaDir = path.join(context.extensionPath, 'lua');
        const cliPath = path.join(pythonDir, 'diplodoc_converter', 'cli.py');

        // Диалоги
        const outputDir = await vscode.window.showInputBox({
            prompt: 'Папка для результата (output)',
            value: path.join(path.dirname(odtPath), 'docs'),
        });
        if (!outputDir) return;

        const useCache = await vscode.window.showQuickPick(['Да (с кэшем)', 'Нет (чистый запуск)'], {
            placeHolder: 'Использовать кэш?'
        });
        if (!useCache) return;

        //TODO: использовать реальный список
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

        const args = [odtPath, outputDir, '--max-heading-level', maxLevel || '6'];

        if (useCache === 'Да (с кэшем)') {
            args.push('--reuse-cache', '--keep-cache');
        }

        args.push('--enable-crossref');

        if (luaFilters) {
            args.push('--lua-filter', luaFilters);
        }

        args.push('--lua-dir', luaDir);

        const terminal = vscode.window.createTerminal({
            name: "Diplodoc Converter",
            cwd: workspaceRoot,
        });
        terminal.show();

        const pythonPathCmd = `$env:PYTHONPATH = "${pythonDir}"`;
        const pythonCmd = `python "${cliPath}" "${args.join('" "')}"`;

        const fullCmd = `${pythonPathCmd}; ${pythonCmd}`;

        console.log("[Diplodoc] Запуск команды:\n", fullCmd);
        terminal.sendText(fullCmd);
    });

    context.subscriptions.push(disposable);
}

function deactivate() { }

module.exports = { activate, deactivate }
