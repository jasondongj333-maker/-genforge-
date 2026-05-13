// 简单测试文件
using System;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;

namespace Test
{
    public class TestCommands
    {
        [CommandMethod("TestCmd")]
        public static void TestCommand()
        {
            Document doc = Application.DocumentManager.MdiActiveDocument;
            doc.Editor.WriteMessage("Test command executed!");
        }
    }
}
