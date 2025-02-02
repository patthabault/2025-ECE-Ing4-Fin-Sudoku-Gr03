using System;
using Python.Runtime;
using Sudoku.Shared;

namespace CCNPythonSimpleSolver;

public class PierreLouisCNNSolverPython : PythonSolverBase

{
    public override SudokuGrid Solve(SudokuGrid s)
    {
        //System.Diagnostics.Debugger.Break();

        //For some reason, the Benchmark runner won't manage to get the mutex whereas individual execution doesn't cause issues
        //using (Py.GIL())
        //{
        // create a Python scope

        var modelPath = System.IO.Path.Combine(Environment.CurrentDirectory, "training/models/sudoku_model.h5");

        using (PyModule scope = Py.CreateScope())
        {

            // Injectez le script de conversion
            AddNumpyConverterScript(scope);

            // Convertissez le tableau .NET en tableau NumPy
            var pyCells = AsNumpyArray(s.Cells, scope);

            // create a Python variable "instance"
            scope.Set("instance", pyCells);
            scope.Set(nameof(modelPath), modelPath);

            // run the Python script
            string code = System.IO.File.ReadAllText("solve_sudoku.py");
            scope.Exec(code);

            PyObject result = scope.Get("solution");

            // Convertissez le résultat NumPy en tableau .NET
            var managedResult = AsManagedArray(scope, result);

            return new SudokuGrid() { Cells = managedResult };
        }
        //}

    }

    

    protected override void InitializePythonComponents()
    {
        //declare your pip packages here
        InstallPipModule("numpy");
        InstallPipModule("tensorflow");
        InstallPipModule("keras");
        base.InitializePythonComponents();
    }

}// didzdkgd