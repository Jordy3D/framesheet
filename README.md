# framesheet

make a sheet of frames  
yeah, that's it

## Example

<img src="https://github.com/Jordy3D/framesheet/assets/19144524/04f43807-cd79-43aa-aad3-51ddd825e611" width=400>

## Example Usage

This script requires the path to the video file as a positional argument. You can also optionally specify the output path, and the number of rows and columns for the framesheet.

Here's an example of how to run the script:

```bash
python framesheet.py my_video.mp4 -o my_framesheet.png -r 5 -c 3
```

Here's a breakdown of the arguments:

### Required Arguments

- `video`: The path to the video file you want to create a framesheet from.

### Optional Arguments

- `-o` or `--output`: The path to save the framesheet to. If not provided, the default is `framesheet.png`, saved in the same directory as the video file.
- `-r` or `--rows`: The number of rows you want in the framesheet. If not provided, the default is `10`.
- `-c` or `--columns`: The number of columns you want in the framesheet. If not provided, the default is `4`.

## Notes

- There are values you can set at the top of the script to change things like font size, padding around the frames, and the maximum size of the framesheet. Your mileage may vary.
- The header section is kind of a mess, but if the values are left as default, it should be fine.
