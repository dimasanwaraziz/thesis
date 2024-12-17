package main

import (
	"crypto/sha256"
	"encoding/hex"
	"flag"
	"fmt"
	"image"
	"image/color"
	_ "image/jpeg"
	"image/png"
	"os"
)

// Fungsi untuk memuat gambar
func loadImage(filePath string) (image.Image, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	img, _, err := image.Decode(file)
	if err != nil {
		return nil, err
	}
	return img, nil
}

// Fungsi untuk menyimpan gambar
func saveImage(img image.Image, filePath string) error {
	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()
	return png.Encode(file, img)
}

// Fungsi untuk mengubah nilai RGBA ke uint8
func rgbaToUint8(c color.Color) (r, g, b, a uint8) {
	r32, g32, b32, a32 := c.RGBA()
	return uint8(r32 >> 8), uint8(g32 >> 8), uint8(b32 >> 8), uint8(a32 >> 8)
}

// Fungsi untuk mengekstrak bit dari byte
func extractBit(messageBits []byte, bitIndex int) byte {
	byteIndex := bitIndex / 8
	bitInByte := bitIndex % 8
	return (messageBits[byteIndex] >> (7 - bitInByte)) & 1
}

// Fungsi untuk menyetel LSB pada nilai warna
func setLSB(value uint8, bit byte) uint8 {
	return (value & 0xFE) | bit
}

// Fungsi untuk menghasilkan key trace menggunakan hash SHA-256
func generateKeyTrace(message string) string {
	hash := sha256.New()
	hash.Write([]byte(message))
	return hex.EncodeToString(hash.Sum(nil))
}

// Fungsi untuk menyembunyikan pesan dalam gambar
func hideMessageInImage(img image.Image, message string) *image.RGBA {
	message += "\000" // Menambahkan terminator null
	messageBits := []byte(message)
	bitIndex := 0
	newImg := image.NewRGBA(img.Bounds())

	// Menyembunyikan pesan dalam gambar
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

	// Menghasilkan key trace dari pesan yang disembunyikan
	keyTrace := generateKeyTrace(message)
	fmt.Println("Generated Key Trace (SHA-256):", keyTrace)

	// Menyimpan key trace dalam file (opsional)
	saveKeyTraceToFile(keyTrace)

	return newImg
}

// Fungsi untuk menyimpan key trace ke file
func saveKeyTraceToFile(keyTrace string) {
	file, err := os.Create("key_trace.txt")
	if err != nil {
		fmt.Println("Error creating key trace file:", err)
		return
	}
	defer file.Close()
	file.WriteString(keyTrace)
	fmt.Println("Key trace saved to file.")
}

// Fungsi untuk mengekstrak pesan dari gambar
func extractMessageFromImage(img image.Image) string {
	var messageBytes []byte
	var currentByte byte
	bitIndex := 0

	// Membaca pesan dari gambar
	for y := 0; y < img.Bounds().Dy(); y++ {
		for x := 0; x < img.Bounds().Dx(); x++ {
			r, g, b, _ := rgbaToUint8(img.At(x, y))

			currentByte = (currentByte << 1) | (r & 1)
			bitIndex++
			if bitIndex == 8 {
				if currentByte == 0 {
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
					return string(messageBytes)
				}
				messageBytes = append(messageBytes, currentByte)
				currentByte = 0
				bitIndex = 0
			}
		}
	}

	// Generate key trace for the decoded message
	decodedMessage := string(messageBytes)
	keyTrace := generateKeyTrace(decodedMessage)
	fmt.Println("Decoded Message Key Trace (SHA-256):", keyTrace)

	return decodedMessage
}

// Fungsi utama
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
