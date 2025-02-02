using System;
using Sudoku.Shared;

namespace Sudoku.Benchmark
{
	public class PierreLouisSolver : ISudokuSolver
	{

		public SudokuGrid Solve(SudokuGrid s)
		{
			Solve(s.Cells);
			return s;
		}

		public bool Solve(int[,] grid)
		{
			for (int row = 0; row < 9; row++)
			{
				for (int col = 0; col < 9; col++)
				{
					if (grid[row, col] == 0)
					{
						for (int num = 1; num <= 9; num++)
						{
							if (IsValid(grid, row, col, num))
							{
								grid[row, col] = num;

								if (Solve(grid))
								{
									return true;
								}

								grid[row, col] = 0; // Backtrack
							}
						}
						return false; // Aucun chiffre ne fonctionne ici
					}
				}
			}
			return true; // Résolu
		}

		private bool IsValid(int[,] grid, int row, int col, int num)
		{
			// Vérifie la ligne
			for (int x = 0; x < 9; x++)
			{
				if (grid[row, x] == num)
				{
					return false;
				}
			}

			// Vérifie la colonne
			for (int x = 0; x < 9; x++)
			{
				if (grid[x, col] == num)
				{
					return false;
				}
			}

			// Vérifie la sous-grille 3x3
			int startRow = row / 3 * 3;
			int startCol = col / 3 * 3;
			for (int i = 0; i < 3; i++)
			{
				for (int j = 0; j < 3; j++)
				{
					if (grid[startRow + i, startCol + j] == num)
					{
						return false;
					}
				}
			}

			return true;
		}



	}
}