use std::slice;
use std::cmp::{min, max};

const THRSHLD: u8 = 127;

fn adderror(b: u8, e: i32) -> u8 {
  min(0xFFi32, max(0x00i32, b as i32 + e)) as u8 // e might be negative so i32
}

/// Rather insecure function to modify image array in place. Passing incorrect
/// height or width arguments will probably cause a segmentation error
///
/// # Arguments
///
/// * `h` - height or array
/// * `w` - width of array
/// * `ptr` - pointer to unsigned char array (i.e. uint8, c_ubyte, c_char_p etc)
/// 
#[no_mangle]
pub extern "C" fn atk(h: i32, w: i32, ptr: *mut u8) {
  assert!(!ptr.is_null());
  let len = h * w;
  let pixels = unsafe {
    slice::from_raw_parts_mut(ptr, len as usize)
  };
  for y in 0..h {
    for x in 0..w {
      let p = y * w + x;
      let old = pixels[p as usize];
      let new = if old > THRSHLD { 0xFFu8 } else { 0x00u8 };
      let err = (old as i32 - new as i32) / 8; // just as fast as `>> 3`
      pixels[p as usize] = new;
      // now distribute the error...
      if (x+1) < w {            // x+1, y
        let px_off = (p + 1) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
      if (x+2) < w {           // x+2, y
        let px_off = (p + 2) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
      if x > 0 && (y+1) < h {   // x-1, y+1
        let px_off = (p + w - 1) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
      if (y+1) < h {           // x, y+1
        let px_off = (p + w) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
      if (x+1) < w && (y+1) < h { // x+1, y+1
        let px_off = (p + w + 1) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
      if (y+2) < h {            // x, y+2
        let px_off = (p + w + w) as usize;
        pixels[px_off] = adderror(pixels[px_off], err);
      }
    }
  }
}
