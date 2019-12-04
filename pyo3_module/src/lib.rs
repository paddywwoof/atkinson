extern crate pyo3;
extern crate ndarray;
extern crate numpy;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use ndarray::ArrayViewMutD;
use numpy::PyArrayDyn;

use std::cmp::{min, max};

const THRSHLD: u8 = 127;

fn adderror(b: u8, e: i32) -> u8 {
  min(0xFFi32, max(0x00i32, b as i32 + e)) as u8 // e might be negative so i32
}

#[pyfunction]
fn atk(imarray: &PyArrayDyn<u8>) {
  let mut pixels: ArrayViewMutD<u8> = imarray.as_array_mut();
  assert!(pixels.ndim() == 2);
  let shp = pixels.shape();
  let (h, w) = (shp[0], shp[1]);
  for y in 0..h {
    for x in 0..w {
      //let p = y * w + x;
      let old = pixels[[y, x]];
      let new = if old > THRSHLD { 0xFFu8 } else { 0x00u8 };
      let err = (old as i32 - new as i32) / 8; // just as fast as `>> 3`
      pixels[[y, x]] = new;
      // now distribute the error...
      if (x+1) < w {            // x+1, y
        pixels[[y, x+1]] = adderror(pixels[[y, x+1]], err);
      }
      if (x+2) < w {           // x+2, y
        pixels[[y, x+2]] = adderror(pixels[[y, x+2]], err);
      }
      if x > 0 && (y+1) < h {   // x-1, y+1
        pixels[[y+1, x-1]] = adderror(pixels[[y+1, x-1]], err);
      }
      if (y+1) < h {           // x, y+1
        pixels[[y+1, x]] = adderror(pixels[[y+1, x]], err);
      }
      if (x+1) < w && (y+1) < h { // x+1, y+1
        pixels[[y+1, x+1]] = adderror(pixels[[y+1, x+1]], err);
      }
      if (y+2) < h {            // x, y+2
        pixels[[y+2, x]] = adderror(pixels[[y+2, x]], err);
      }
    }
  }
}

#[pymodule]
fn atk_mod_rm(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(atk))?;

    Ok(())
}
