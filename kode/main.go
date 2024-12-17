package main

import (
	"flag"
	"fmt"
	"image"
	"image/color"
	_ "image/jpeg"
	"image/png"
	"os"
)

// Fungsi utama untuk encoding pesan ke gambar
func hideMessageInImage(img image.Image, message string) *image.RGBA {
	message += "\000" // Menambahkan terminator
	messageBits := []byte(message)
	bitIndex := 0
	newImg := image.NewRGBA(img.Bounds())

	fmt.Println("=== DEBUG ENCODING START ===")
	fmt.Printf("Message to encode: %s\n", message)
	fmt.Printf("Total bits to encode: %d\n", len(messageBits)*8)

	for y := 0; y < img.Bounds().Dy(); y++ {
		for x := 0; x < img.Bounds().Dx(); x++ {
			if bitIndex >= len(messageBits)*8 {
				newImg.Set(x, y, img.At(x, y))
				continue
			}

			r, g, b, a := rgbaToUint8(img.At(x, y))

			r = setLSB(r, extractBit(messageBits, bitIndex))
			bitIndex++
			if bitIndex < len(messageBits)*8 {
				g = setLSB(g, extractBit(messageBits, bitIndex))
				bitIndex++
			}
			if bitIndex < len(messageBits)*8 {
				b = setLSB(b, extractBit(messageBits, bitIndex))
				bitIndex++
			}

			newImg.Set(x, y, color.RGBA{r, g, b, a})
		}
	}
	fmt.Println("=== DEBUG ENCODING END ===")
	return newImg
}

// Fungsi utama untuk decoding pesan dari gambar
func extractMessageFromImage(img image.Image) string {
	var messageBytes []byte
	var currentByte byte
	bitIndex := 0

	fmt.Println("=== DEBUG DECODING START ===")
	for y := 0; y < img.Bounds().Dy(); y++ {
		for x := 0; x < img.Bounds().Dx(); x++ {
			r, g, b, _ := rgbaToUint8(img.At(x, y))

			currentByte = (currentByte << 1) | (r & 1)
			bitIndex++
			if bitIndex == 8 {
				if currentByte == 0 {
					fmt.Println("=== DEBUG DECODING END ===")
					return string(messageBytes)
				}
				messageBytes = append(messageBytes, currentByte)
				currentByte = 0
				bitIndex = 0
			}

			currentByte = (currentByte << 1) | (g & 1)
			bitIndex++
			if bitIndex == 8 {
				if currentByte == 0 {
					fmt.Println("=== DEBUG DECODING END ===")
					return string(messageBytes)
				}
				messageBytes = append(messageBytes, currentByte)
				currentByte = 0
				bitIndex = 0
			}

			currentByte = (currentByte << 1) | (b & 1)
			bitIndex++
			if bitIndex == 8 {
				if currentByte == 0 {
					fmt.Println("=== DEBUG DECODING END ===")
					return string(messageBytes)
				}
				messageBytes = append(messageBytes, currentByte)
				currentByte = 0
				bitIndex = 0
			}
		}
	}
	fmt.Println("=== DEBUG DECODING END ===")
	return string(messageBytes)
}

// Helper untuk ekstrak bit dari array byte
func extractBit(data []byte, index int) uint8 {
	return (data[index/8] >> (7 - uint(index%8))) & 1
}

// Helper untuk mengatur LSB pada byte
func setLSB(value, bit uint8) uint8 {
	return (value & 0xFE) | bit
}

// Helper untuk mengubah nilai RGBA menjadi uint8
func rgbaToUint8(c color.Color) (r, g, b, a uint8) {
	r32, g32, b32, a32 := c.RGBA()
	return uint8(r32 >> 8), uint8(g32 >> 8), uint8(b32 >> 8), uint8(a32 >> 8)
}

// Fungsi load gambar
func loadImage(filename string) (image.Image, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	img, format, err := image.Decode(file)
	if err != nil {
		return nil, err
	}
	fmt.Println("Loaded image format:", format)
	return img, nil
}

// Fungsi save gambar
func saveImage(img *image.RGBA, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()
	return png.Encode(file, img)
}

func main() {
	mode := flag.String("mode", "encode", "Mode: encode or decode")
	inputImage := flag.String("input", "", "Input image file")
	outputImage := flag.String("output", "output.png", "Output image file")
	message := flag.String("message", "", "Message to hide (encode mode only)")
	flag.Parse()

	if *mode == "encode" {
		if *inputImage == "" || *message == "" {
			fmt.Println("Usage: -mode encode -input <input.png> -output <output.png> -message <message>")
			return
		}
		img, err := loadImage(*inputImage)
		if err != nil {
			fmt.Println("Error loading image:", err)
			return
		}
		encodedImg := hideMessageInImage(img, *message)
		if err := saveImage(encodedImg, *outputImage); err != nil {
			fmt.Println("Error saving image:", err)
			return
		}
		fmt.Println("Pesan berhasil disisipkan ke gambar:", *outputImage)
	} else if *mode == "decode" {
		if *inputImage == "" {
			fmt.Println("Usage: -mode decode -input <encoded.png>")
			return
		}
		img, err := loadImage(*inputImage)
		if err != nil {
			fmt.Println("Error loading image:", err)
			return
		}
		message := extractMessageFromImage(img)
		fmt.Println("Pesan yang disembunyikan:", message)
	} else {
		fmt.Println("Mode tidak dikenal. Gunakan 'encode' atau 'decode'.")
	}
}
