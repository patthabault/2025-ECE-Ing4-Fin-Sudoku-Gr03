namespace Sudoku.Z3Solvers;

public class Z3ParallelPythonSolver : Z3SimplePythonSolver
{
	protected override string GetPythonScript()
	{
		string code = System.IO.File.ReadAllText("z3solver_advanced.py");
		return code;
	}
}