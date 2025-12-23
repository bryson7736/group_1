import pytest
from grid import Grid
from settings import GRID_COLS, GRID_ROWS

class MockGame:
    pass

@pytest.fixture
def grid():
    game = MockGame()
    return Grid(game)

def test_grid_initialization(grid):
    assert grid.cols == GRID_COLS
    assert grid.rows == GRID_ROWS
    assert len(grid.cells) == GRID_COLS
    assert len(grid.cells[0]) == GRID_ROWS

def test_grid_bounds(grid):
    assert grid.in_bounds(0, 0)
    assert grid.in_bounds(GRID_COLS - 1, GRID_ROWS - 1)
    assert not grid.in_bounds(-1, 0)
    assert not grid.in_bounds(GRID_COLS, 0)

def test_grid_set_get_remove(grid):
    assert grid.get(0, 0) is None
    
    obj = "TestObject"
    grid.set(0, 0, obj)
    assert grid.get(0, 0) == obj
    
    grid.remove(0, 0)
    assert grid.get(0, 0) is None

def test_grid_empty_cells(grid):
    # Initially full empty
    empty = grid.get_empty_cells()
    assert len(empty) == GRID_COLS * GRID_ROWS
    
    grid.set(0, 0, "obj")
    empty_after = grid.get_empty_cells()
    assert len(empty_after) == (GRID_COLS * GRID_ROWS) - 1
    assert (0, 0) not in empty_after
