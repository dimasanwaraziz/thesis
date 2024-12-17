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

// Fungsi encode
func encode(inputImage, outputImage, message string) {
	img, err := loadImage(inputImage)
	if err != nil {
		fmt.Println("Error loading image:", err)
		return
	}
	encodedImg := hideMessageInImage(img, message)
	err = saveImage(encodedImg, outputImage)
	if err != nil {
		fmt.Println("Error saving image:", err)
		return
	}
	fmt.Println("Pesan berhasil disisipkan ke gambar:", outputImage)
}

// Fungsi decode
func decode(inputImage string) {
	img, err := loadImage(inputImage)
	if err != nil {
		fmt.Println("Error loading image:", err)
		return
	}
	message := extractMessageFromImage(img)
	fmt.Println("Pesan yang disembunyikan:", message)
}

// Fungsi loadImage yang mendukung JPG dan PNG
func loadImage(filename string) (image.Image, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	// Decode gambar dengan format PNG atau JPG
	img, format, err := image.Decode(file)
	if err != nil {
		return nil, err
	}

	fmt.Println("Loaded image format:", format)
	return img, nil
}

// Fungsi saveImage yang menyimpan hanya dalam format PNG
func saveImage(img image.Image, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	// Selalu menyimpan dalam format PNG
	return png.Encode(file, img)
}

func hideMessageInImage(img image.Image, message string) image.Image {
	message += "\000" // Tambahkan terminator
	messageBits := []byte(message)
	bitIndex := 0
	newImg := image.NewRGBA(img.Bounds())

	fmt.Println("=== DEBUG ENCODING START ===")
	fmt.Printf("Message to encode: %s\n", message)
	fmt.Printf("Total bits to encode: %d\n", len(messageBits)*8)

	for y := 0; y < img.Bounds().Dy(); y++ {
		for x := 0; x < img.Bounds().Dx(); x++ {
			r, g, b, a := img.At(x, y).RGBA()

			if bitIndex < len(messageBits)*8 {
				oldR := r
				r = (r & 0xFFFE) | uint32((messageBits[bitIndex/8]>>(7-(bitIndex%8)))&1)
				fmt.Printf("Pixel (%d, %d) - R: %d -> %d\n", x, y, oldR&1, r&1)
				bitIndex++
			}

			if bitIndex < len(messageBits)*8 {
				oldG := g
				g = (g & 0xFFFE) | uint32((messageBits[bitIndex/8]>>(7-(bitIndex%8)))&1)
				fmt.Printf("Pixel (%d, %d) - G: %d -> %d\n", x, y, oldG&1, g&1)
				bitIndex++
			}

			if bitIndex < len(messageBits)*8 {
				oldB := b
				b = (b & 0xFFFE) | uint32((messageBits[bitIndex/8]>>(7-(bitIndex%8)))&1)
				fmt.Printf("Pixel (%d, %d) - B: %d -> %d\n", x, y, oldB&1, b&1)
				bitIndex++
			}

			newColor := color.RGBA{uint8(r >> 8), uint8(g >> 8), uint8(b >> 8), uint8(a >> 8)}
			newImg.Set(x, y, newColor)
		}
	}

	fmt.Println("=== DEBUG ENCODING END ===")
	return newImg
}

func extractMessageFromImage(img image.Image) string {
	var messageBytes []byte
	currentByte := byte(0)
	bitIndex := 0

	fmt.Println("=== DEBUG DECODING START ===")

	for y := 0; y < img.Bounds().Dy(); y++ {
		for x := 0; x < img.Bounds().Dx(); x++ {
			r, g, b, _ := img.At(x, y).RGBA()

			// Ekstrak bit LSB dari R, G, B
			currentByte = (currentByte << 1) | byte(r&1)
			fmt.Printf("Pixel (%d, %d) - R: %d, CurrentByte: %08b\n", x, y, r&1, currentByte)
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

			currentByte = (currentByte << 1) | byte(g&1)
			fmt.Printf("Pixel (%d, %d) - G: %d, CurrentByte: %08b\n", x, y, g&1, currentByte)
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

			currentByte = (currentByte << 1) | byte(b&1)
			fmt.Printf("Pixel (%d, %d) - B: %d, CurrentByte: %08b\n", x, y, b&1, currentByte)
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
		encode(*inputImage, *outputImage, *message)
	} else if *mode == "decode" {
		if *inputImage == "" {
			fmt.Println("Usage: -mode decode -input <encoded.png>")
			return
		}
		decode(*inputImage)
	} else {
		fmt.Println("Mode tidak dikenal. Gunakan 'encode' atau 'decode'.")
	}
}
